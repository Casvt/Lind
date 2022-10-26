#-*- coding: utf-8 -*-

class LindNotFound(Exception):
	"""The Lind with the given id was not found
	"""
	api_response = {'error': 'LindNotFound', 'result': {}}, 404
	
class InvalidExpirationTime(Exception):
	"""The expiration time was in the past
	"""
	api_response = {'error': 'InvalidExpirationTime', 'result': {}}, 400
	
class InvalidLimitUsage(Exception):
	"""The limit usage value was equal or below 0
	"""
	api_response = {'error': 'InvalidLimitUsage', 'result': {}}, 400

class AccessUnauthorized(Exception):
	"""Access to the Lind was not allowed because the password to access it was not correct
	"""
	api_response = {'error': 'AccessUnauthorized', 'result': {}}, 401
	
class NotManageable(Exception):
	"""It's not possible to manage a Lind that doesn't have an admin_password setup
	"""
	api_response = {'error': 'NotManageable', 'result': {}}, 400