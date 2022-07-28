#-*- coding: utf-8 -*-

class InvalidExpirationTime(Exception):
	"""The expiration time given is now or in the past
	"""
	pass

class InvalidLimitUsage(Exception):
	"""The value for the usage limiter is invalid (0 or lower)
	"""
	pass

class LindIdNotFound(Exception):
	"""A lind is requested but the id is not found in the database
	"""
	pass

class AccessUnauthorized(Exception):
	"""Unauthorized access to a lind with the intention to access it (password not given or invalid)
	"""
	pass

class ManageUnauthorized(Exception):
	"""Unauthorized access to a lind with the intention to manage it (password not given or invalid)
	"""
	pass

class NotManageable(Exception):
	"""Lind is not manageble because no admin password was set
	but an attempt was made to manage it
	"""
	pass
