#-*- coding: utf-8 -*-

from backend.custom_exceptions import *

from random import choice
from hashlib import pbkdf2_hmac
from os import urandom
from time import time
from sqlite3 import connect as db_connect
from sqlite3 import IntegrityError

LIND_RATE_LIMIT = 60 		# x creations per minute alowed per ip address
LIND_ID_MIN_LENGTH = 5 		# the minimal length of the lind id; adviced to leave at 5
LIND_DB_FILE = 'Lind.db' 	# the name (and location) of the database file
LIND_ID_RANGE = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789' #the characters that the lind id can consist of

LIND_TABLE_KEYS = ['lind','url','expiration_time','limit_usage','access_password','admin_password'] #don't touch

def startup() -> None:
	"""Setup application when starting up

	Returns:
		None
	"""
	db = db_connect(LIND_DB_FILE)
	cursor = db.cursor()
	
	table_creation = """
		CREATE TABLE IF NOT EXISTS links(
			lind VARCHAR(10) PRIMARY KEY,
			url TEXT NOT NULL,
			expiration_time INTEGER(8),
			limit_usage INTEGER,
			access_password BLOB,
			admin_password BLOB
		);
		CREATE TABLE IF NOT EXISTS rate_limiter(
			ip VARCHAR(15) PRIMARY KEY,
			visit_count INTEGER,
			expiration_time INTEGER(8)
		);
	"""
	cursor.executescript(table_creation)
	db.commit()
	return None

def database_maintenance(full: bool=True) -> None:
	"""Commit and optionally cleanup the database file

	Args:
		full (bool, optional): Cleanup the database on top of commiting. Defaults to True.

	Returns:
		None
	"""
	db = db_connect(LIND_DB_FILE)
	cursor = db.cursor()

	if full == True:
		database_cleaner = f"""
			DELETE FROM rate_limiter WHERE expiration_time < {time() - 120};
			DELETE FROM links WHERE expiration_time < {time()};
		"""
		cursor.executescript(database_cleaner)

	cursor.close()
	db.commit()
	db.close()
	return None

def rate_limiter(ip: str) -> tuple:
	"""Check if an ip follows the rate limit rules

	Args:
		ip (str): The ip to check for

	Returns:
		tuple: [0] is wether or not the request is approved (if the client has reached it's rate limit or not), [1] is the timeout in case the client has reached the limit
	"""
	db = db_connect(LIND_DB_FILE)
	cursor = db.cursor()
	
	cursor.execute("SELECT * FROM rate_limiter WHERE ip = ?", (ip,))
	result = cursor.fetchone()
	if result == None:
		#first visit of ip
		cursor.execute("INSERT INTO rate_limiter VALUES (?,?,?)", (ip, 1, time() + 60))
		decision = 'APPROVED', -1
	else:
		#ip has already requested before
		if time() < result[2]:
			if result[1] == LIND_RATE_LIMIT:
				#rate limit reached for ip
				decision = 'DISAPPROVED', result[2] - time()
			else:
				#request allowed
				cursor.execute("UPDATE rate_limiter SET visit_count = ? WHERE ip = ?", (result[1] + 1, ip))
				decision = 'APPROVED', -1
		else:
			#60s have passed so reset counter
			cursor.execute("UPDATE rate_limiter SET visit_count = ?, expiration_time = ? WHERE ip = ?", (1, time() + 60, ip))
			decision = 'APPROVED', -1

	db.commit()
	return decision

def register_url(
	url: str,
	expiration_time: int = -1,
	limit_usage: int = -1,
	access_password: str = None,
	admin_password: str = None,
) -> str:
	"""Generate a new lind id

	Args:
		url (str): The url to shorten
		expiration_time (int, epoch time, optional): The epoch time after which the lind expires. Defaults to -1.
		limit_usage (int, optional): The amount of times a lind can be used before it expires. Defaults to -1.
		access_password (str, optional): The password to be entered in order for the user to access the link. Defaults to None.
		admin_password (str, optional): The password needed if you want to be able to edit the link afterwards. Defaults to None.

	Raises:
		InvalidExpirationTime: The expiration time given is now or in the past
		InvalidLimitUsage: The value for the usage limiter is invalid (0 or lower)

	Returns:
		str: Lind id

	If admin_password is given, the user can manage the lind by going to {lind_url}/manage and entering the password.
	There is no way to edit or recover the admin_password in the case of losing it.
	"""
	db = db_connect(LIND_DB_FILE)
	cursor = db.cursor()

	#get current lind id length
	cursor.execute("SELECT LENGTH(lind) FROM links ORDER BY lind DESC LIMIT 1;")
	lind_id_length = cursor.fetchone()[0] or LIND_ID_MIN_LENGTH

	#check if every possibility with this length hasn't been used yet
	cursor.execute("SELECT COUNT(*) FROM links WHERE LENGTH(lind) = ?;", (lind_id_length,))
	if len(LIND_ID_RANGE) ** lind_id_length == cursor.fetchone()[0]:
		lind_id_length += 1

	insert_keys = ['url']
	insert_values = [url]

	if expiration_time != -1:
		#check if expiration time is valid
		if int(expiration_time) <= time():
			raise InvalidExpirationTime(f'{expiration_time} is now or in the past')

		insert_keys.append('expiration_time')
		insert_values.append(expiration_time)

	if limit_usage != -1:
		#check if usage limiter has valid value
		if int(limit_usage) <= 0:
			raise InvalidLimitUsage(f'{limit_usage} is equal to, or below 0')
		
		insert_keys.append('limit_usage')
		insert_values.append(limit_usage)

	#handle passwords
	if access_password != None:
		#hash access password
		salt = urandom(32)
		hash = pbkdf2_hmac('sha256', access_password.encode('utf-8'), salt, 100000)
		access_password = salt + hash
		
		insert_keys.append('access_password')
		insert_values.append(access_password)
	
	if admin_password != None:
		#hash admin password
		salt = urandom(32)
		hash = pbkdf2_hmac('sha256', admin_password.encode('utf-8'), salt, 100000)
		admin_password = salt + hash
		
		insert_keys.append('admin_password')
		insert_values.append(admin_password)

	#insert entry into database with lind id
	insert_keys = ','.join(insert_keys)
	insert_questions = ','.join(['?'] * len(insert_values))
	while 1:
		lind_id = ''.join(choice(LIND_ID_RANGE) for _ in range(lind_id_length))
		if lind_id in ('api','create'): continue
		try:
			cursor.execute(
				f"""
				INSERT INTO links({insert_keys}, lind)
				VALUES ({insert_questions}, ?)
				""",
				insert_values + [lind_id]
			)
		except IntegrityError:
			continue
		break

	db.commit()
	return lind_id

def get_url(
	lind_id: str,
	intention: str,
	access_password: str = None,
	admin_password: str = None
):
	"""Get a lind

	Args:
		lind_id (str): The id of the lind to get
		intention (str): What you want to do with the lind ('access' or 'manage')
		access_password (str, optional): The password to access the lind in the case one is set and 'access' is the intention. Defaults to None.
		admin_password (str, optional): The password to manage the lind in the case that 'manage' is the intention. Defaults to None.

	Raises:
		LindIdNotFound: The given lind id is not found in the database
		AccessUnauthorized: A password is set for the lind to access it and it was not given or invalid
		NotManageable: The user tries to manage a lind that doesn't support managing because it didn't have an admin_password set when registering it
		ManageUnauthorized: Password given to manage lind is not given or invalid

	Returns:
		str (access): url
		dict (manage): lind info
	"""
	db = db_connect(LIND_DB_FILE)
	cursor = db.cursor()

	if not intention in ('access','manage'):
		return f'Invalid Intention: {intention}'

	#fetch entry from database based on lind id
	cursor.execute("SELECT * FROM links WHERE lind = ?", (lind_id,))
	result = cursor.fetchone()
	if result == None:
		#no entry found
		raise LindIdNotFound

	if (result[2] != None and int(result[2]) < time()) or (result[3] != None and int(result[3]) == 0):
		#entry has expired
		cursor.execute("DELETE FROM links WHERE lind = ?", (lind_id,))
		db.commit()
		raise LindIdNotFound

	if intention == 'access':
		if result[4] != None:
			#lind has password restriction
			if access_password == None:
				raise AccessUnauthorized('No password given')
			else:
				attempt = pbkdf2_hmac('sha256', access_password.encode('utf-8'), result[4][:32], 100000)
				if not attempt == result[4][32:]:
					raise AccessUnauthorized('Invalid password given')		

		if result[3] != None:
			cursor.execute("UPDATE links SET limit_usage = ? WHERE lind = ?", (int(result[3]) - 1,lind_id))
			db.commit()

		return result[1]
	
	if intention == 'manage':
		if result[5] == None:
			#lind is not manageable
			raise NotManageable
		else:
			if admin_password == None:
				raise ManageUnauthorized('No password given')
			else:
				attempt = pbkdf2_hmac('sha256', admin_password.encode('utf-8'), result[5][:32], 100000)
				if not attempt == result[5][32:]:
					raise ManageUnauthorized('Invalid password given')
		return dict(zip(LIND_TABLE_KEYS[:4], result[:4]))

def edit_url(
	lind_id: str,
	url: str = None,
	expiration_time: int = -1,
	limit_usage: int = -1,
	access_password: str = None,
	admin_password: str = None
) -> dict:
	"""Edit a lind

	Args:
		lind_id (str): The id of the lind to edit
		url (str, optional): The new value for the url. Defaults to None.
		expiration_time (int, epoch time, optional): The new value for the expiration time. Defaults to -1.
		limit_usage (int, optional): The new value for the usage limiter. Defaults to -1.
		access_password (str, optional): The new value for the access password. Defaults to None.
		admin_password (str, optional): The new value for the admin password. Defaults to None.

	Raises:
		LindIdNotFound: The given lind id is not found in the database
		InvalidExpirationTime: The expiration time given is now or in the past
		InvalidLimitUsage: The value for the usage limiter is invalid (0 or lower)

	Returns:
		dict: lind info
	"""
	db = db_connect(LIND_DB_FILE)
	cursor = db.cursor()

	#fetch entry from database based on lind id
	cursor.execute("SELECT * FROM links WHERE lind = ?", (lind_id,))
	result = cursor.fetchone()
	if result == None:
		#no entry found
		raise LindIdNotFound

	if result[2] != None and int(result[2]) < time():
		#entry has expired
		cursor.execute("DELETE FROM links WHERE lind = ?", (lind_id,))
		db.commit()
		raise LindIdNotFound

	insert_keys = []
	insert_values = []

	if url != None:
		insert_keys.append('url = ?')
		insert_values.append(url)

	if expiration_time != -1:
		#check if expiration time is valid
		if int(expiration_time) <= time():
			raise InvalidExpirationTime(f'{expiration_time} is now or in the past')

		insert_keys.append('epiration_time = ?')
		insert_values.append(expiration_time)

	if limit_usage != -1:
		#check if usage limiter has valid value
		if int(limit_usage) <= 0:
			raise InvalidLimitUsage(f'{limit_usage} is equal to, or below 0')
		
		insert_keys.append('limit_usage = ?')
		insert_values.append(limit_usage)

	#handle passwords
	if access_password != None:
		#hash access password
		salt = urandom(32)
		hash = pbkdf2_hmac('sha256', access_password.encode('utf-8'), salt, 100000)
		access_password = salt + hash

		insert_keys.append('access_password = ?')
		insert_values.append(access_password)
	
	if admin_password != None:
		#hash admin password
		salt = urandom(32)
		hash = pbkdf2_hmac('sha256', admin_password.encode('utf-8'), salt, 100000)
		admin_password = salt + hash

		insert_keys.append('admin_password = ?')
		insert_values.append(admin_password)

	if insert_keys:
		cursor.execute(f"UPDATE links SET {','.join(insert_keys)} WHERE lind = ?;", insert_values + [lind_id])
		db.commit()
	cursor.execute(f"SELECT * FROM links WHERE lind = ?;", (lind_id,))
	result = cursor.fetchone()
	return dict(zip(LIND_TABLE_KEYS[:4], result[:4]))
