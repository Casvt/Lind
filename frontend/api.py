# -*- coding: utf-8 -*-

from flask import Blueprint, request
from backend.custom_exceptions import (
	AccessUnauthorized,
	InvalidExpirationTime,
	InvalidLimitUsage,
	LindNotFound,
	NotManageable,
)
from backend.db import maintain_db
from backend.lind import Lind, register_lind

api = Blueprint("api", __name__)
db_maintenance = maintain_db()

@api.before_request
def api_maintenance_check():
	db_maintenance.check_maintenance()

@api.route("/create", methods=["POST"])
def api_create():
	"""
	/api/create:
		POST:
			Description: Create a Lind
			Arguments:
				Body (Content-Type: application/json):
					url (str, required): the url to shorten
					expiration_time (date: YYYY-MM-DDTHH:MM): Date and time after which the Lind will expire and will automatically be deleted
					limit_usage (int): The amount of times a Lind can be used before it expires and it automatically gets deleted
					access_password (str): The password that is required to be entered before a user gets redirected
					admin_password (str): The password that if set allows you to manage the Lind afterwards by going to /<lind_id>/manage. You can then edit settings of the Lind.
			Returns:
				Info about newly created Lind including the essential lind_id, with which you use the lind
	"""
	data = request.get_json()

	# check if url is given
	if not "url" in data:
		return {"error": "KeyNotFound", "result": {"key": "url"}}, 400

	try:
		# register lind
		result = register_lind(
			url=data.get("url"),
			expiration_time=data.get("expiration_time") or None,
			limit_usage=data.get("limit_usage") or None,
			access_password=data.get("access_password") or None,
			admin_password=data.get("admin_password") or None,
		)

	except (InvalidExpirationTime, InvalidLimitUsage) as e:
		return e.api_response

	else:
		return {"error": None, "result": result}, 201

@api.route("/<lind_id>", methods=["GET"])
def api_get_lind(lind_id: str):
	"""
	/api/<lind_id>:
		NOTE: Replace <lind_id> with the lind id, e.g. /api/Zf76D
		GET:
			Description: Get the underlying url of the Lind
			Arguments:
				URL:
					access_password (str): In the case that the Lind is password protected for access, the password should be given with this argument
			Returns:
				The underlying url of the Lind
	"""	
	access_password = request.values.get('access_password')
	try:
		lind = Lind(lind_id, access_password=access_password)
		return {"error": None, "result": dict(lind)}, 200
	except (LindNotFound, AccessUnauthorized) as e:
		return e.api_response

@api.route("/<lind_id>/manage", methods=["GET", "PUT", "DELETE"])
def api_lind(lind_id: str):
	"""
	/api/<lind_id>/manage:
		NOTE: Replace <lind_id> with the lind id, e.g. /api/kWz8A/manage
		NOTE 2: This endpoint can only be used when admin_password was set when creating the Lind
		GET:
			Description: Get info on a Lind
			Arguments:
				URL:
					admin_password (str, required): The admin password set when the Lind got created in order to manage the Lind afterwards
			Returns:
				Info about the Lind.
				access_password and admin_password are not included in the output, however you can still edit them when using the PUT method.
		PUT:
			Description: Edit Lind. Give keys and their new values to edit the Lind.
			Arguments:
				URL:
					admin_password (str, required): The admin password set when the Lind got created in order to manage the Lind afterwards
				Body (Content-Type: application/json):
					url (str, required): the url to shorten
					expiration_time (date: YYYY-MM-DDTHH:MM): Date and time after which the Lind will expire and will automatically be deleted
					limit_usage (int): The amount of times a Lind can be used before it expires and it automatically gets deleted
					access_password (str): The new password that is required to be entered before a user gets redirected
					admin_password (str): The new password that if set allows you to manage the Lind afterwards by going to /<lind_id>/manage. You can then edit settings of the Lind.
			Returns:
				Info about Lind with new values applied
		DELETE:
			Description: Delete Lind.
			Arguments:
				URL:
					admin_password (str, required): The admin password set when the Lind got created in order to manage the Lind afterwards
			Returns:
				Nothing. Lind was deleted succesfully
	"""

	try:
		admin_password = request.values.get("admin_password")
		if admin_password == None:
			return {"error": "KeyNotFound", "result": {"key": "admin_password"}}, 400

		lind = Lind(lind_id, admin_password=admin_password)

		if request.method == "GET":
			return {"error": None, "result": dict(lind)}, 200

		elif request.method == "PUT":
			data = request.get_json()
			update_values = {
				"url": data.get("url"),
				"expiration_time": data.get("expiration_time") or None,
				"limit_usage": data.get("limit_usage") or None,
				"access_password": data.get("access_password") or None,
				"admin_password": data.get("admin_password") or None,
			}
			result = lind.update(update_values)
			return {"error": None, "result": result}, 200

		elif request.method == "DELETE":
			lind.delete()
			return {"error": None, "result": {}}, 200

	except (
		LindNotFound,
		AccessUnauthorized,
		NotManageable,
		InvalidExpirationTime,
		InvalidLimitUsage,
	) as e:
		return e.api_response
