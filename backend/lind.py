# -*- coding: utf-8 -*-

from datetime import datetime
from hashlib import pbkdf2_hmac
from os import urandom
from random import choice
from sqlite3 import IntegrityError
from time import time

from backend.custom_exceptions import (
	AccessUnauthorized,
	InvalidExpirationTime,
	InvalidLimitUsage,
	LindNotFound,
	NotManageable,
)
from backend.db import get_db

LIND_ID_MIN_LENGTH = 5  # the minimal length of the lind id; adviced to leave at 5
LIND_ID_RANGE = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"  # the characters that the lind id can consist of
LIND_HASH_ITERATIONS = 100_000

not_allowed_ids = ("api", "create", "use", "manage", "api-docs")
not_allowed_ids_lengths = {
	len(x): len([y for y in not_allowed_ids if len(y) == len(x)])
	for x in not_allowed_ids
}

def _format_data(data: dict) -> dict:
	if data.get('expiration_time') is not None:
		if isinstance(data.get('expiration_time'), str):
			data['expiration_time'] = datetime.strptime(
				data["expiration_time"], "%Y-%m-%dT%H:%M"
			).timestamp()
			if 0 <= data['expiration_time'] <= time():
				raise InvalidExpirationTime
		else:
			raise InvalidExpirationTime

	if data.get('limit_usage') is not None:
		if not (isinstance(data.get('limit_usage'), int) and 1 <= data['limit_usage']):
			raise InvalidLimitUsage
			
	if data.get('access_password') is not None:
		salt = urandom(32)
		hash = pbkdf2_hmac(
			"sha256", data['access_password'].encode(), salt, LIND_HASH_ITERATIONS
		)
		data["access_password"] = salt + hash
		
	if data.get('admin_password') is not None:
		salt = urandom(32)
		hash = pbkdf2_hmac(
			"sha256", data['admin_password'].encode(), salt, LIND_HASH_ITERATIONS
		)
		data["admin_password"] = salt + hash
		
	return data

class AccessLind:
	def __init__(self, lind_id: str):
		self.lind_id = lind_id

	def __iter__(self) -> iter:
		cursor = get_db(output_type='dict')
		cursor.execute("SELECT url, limit_usage FROM linds WHERE lind_id = ?", (self.lind_id,))
		result = cursor.fetchone()

		if result['limit_usage'] is not None:
			if 2 <= result['limit_usage']:
				cursor.execute("UPDATE linds SET limit_usage = ? WHERE lind_id = ?", (result['limit_usage'] - 1, self.lind_id))
			if result['limit_usage'] == 1:
				cursor.execute("DELETE FROM linds WHERE lind_id = ?", (self.lind_id,))

		return iter([('url', result['url'])])

class ManageLind:
	def __init__(self, lind_id: str):
		self.lind_id = lind_id

	def __iter__(self) -> iter:
		cursor = get_db(output_type='dict')
		cursor.execute("SELECT url, expiration_time, limit_usage FROM linds WHERE lind_id = ?", (self.lind_id,))
		result = dict(cursor.fetchone())

		return iter(result.items())

	def update(self, data: dict) -> dict:
		cursor = get_db(output_type='dict')
		cursor.execute("SELECT url, expiration_time, limit_usage, access_password, admin_password FROM linds WHERE lind_id = ?", (self.lind_id,))
		current_data = dict(cursor.fetchone())

		data = {k: v for k, v in _format_data(data).items() if v is not None}
		current_data.update(data)
		
		cursor.execute(
			"UPDATE linds SET url=?, expiration_time=?, limit_usage=?, access_password=?, admin_password=? WHERE lind_id = ?;",
			(current_data['url'], current_data['expiration_time'], current_data['limit_usage'], current_data['access_password'], current_data['admin_password'], self.lind_id)
		)
		
		return dict(self)

	def delete(self) -> None:
		cursor = get_db()
		cursor.execute("DELETE FROM linds WHERE lind_id = ?", (self.lind_id,))
		return

def Lind(lind_id: str, access_password: str=None, admin_password: str=None):
	cursor = get_db(output_type='dict')
	cursor.execute("SELECT expiration_time, limit_usage, access_password, admin_password FROM linds WHERE lind_id = ?", (lind_id,))
	result = cursor.fetchone()
	if result is None:
		raise LindNotFound

	if result['expiration_time'] is not None and result['expiration_time'] < time():
		cursor.execute("DELETE FROM linds WHERE lind_id = ?", (lind_id,))
		raise LindNotFound

	if (access_password is None and admin_password is None) or access_password is not None:
		#access lind
		if result['access_password'] is not None:
			#access is password protected
			if access_password is None:
				raise AccessUnauthorized
			attempt = pbkdf2_hmac('sha256', access_password.encode(), result['access_password'][:32], LIND_HASH_ITERATIONS)
			if attempt != result['access_password'][32:]:
				raise AccessUnauthorized

		return AccessLind(lind_id)

	elif admin_password is not None:
		#manage lind
		if result['admin_password'] is None:
			raise NotManageable
		attempt = pbkdf2_hmac('sha256', admin_password.encode(), result['admin_password'][:32], LIND_HASH_ITERATIONS)
		if attempt != result['admin_password'][32:]:
			raise AccessUnauthorized

		return ManageLind(lind_id)

def register_lind(
	url: str,
	expiration_time: int = None,
	limit_usage: int = None,
	access_password: str = None,
	admin_password: str = None,
) -> dict:
	cursor = get_db()

	# get current lind_id length
	cursor.execute("SELECT LENGTH(lind_id) FROM linds ORDER BY rowid DESC LIMIT 1;")
	lind_id_length = next(iter(cursor.fetchone() or [LIND_ID_MIN_LENGTH]))

	# check if every possibility with this length hasn't been used yet
	cursor.execute(
		"SELECT COUNT(rowid) FROM linds WHERE LENGTH(lind_id) = ?;", (lind_id_length,)
	)
	if len(LIND_ID_RANGE) ** lind_id_length - not_allowed_ids_lengths.get(lind_id_length, 0) == cursor.fetchone()[0]:
		lind_id_length += 1

	data = {
		'url': url,
		'expiration_time': expiration_time,
		'limit_usage': limit_usage,
		'access_password': access_password,
		'admin_password': admin_password
	}
	data = _format_data(data)

	# keep generating an id and trying to insert it in the db until it's allowed (it's not already in use)
	# basically "try until you accidentally get a valid non-used lind_id"
	# this guessing seems ineffecient but proves to be very fast
	while 1:
		lind_id = "".join(choice(LIND_ID_RANGE) for _ in range(lind_id_length))
		if lind_id in not_allowed_ids:
			continue
		try:
			cursor.execute(
				"""
				INSERT INTO linds(lind_id, url, expiration_time, limit_usage, access_password, admin_password)
				VALUES (?,?,?,?,?,?);
			""", (
				lind_id,
				data["url"],
				data["expiration_time"],
				data["limit_usage"],
				data["access_password"],
				data["admin_password"],
			))
		except IntegrityError:
			continue
		break

	data["access_password"] = access_password
	data["admin_password"] = admin_password
	data["lind_id"] = lind_id

	return data
