#-*- coding: utf-8 -*-

from backend.backend import edit_url, register_url, get_url, rate_limiter, LIND_RATE_LIMIT
from backend.custom_exceptions import *

from flask import Blueprint, request, render_template
from datetime import datetime

api = Blueprint('api',__name__)

#add endpoints
@api.route('/', methods=['GET'])
def api_root():
	return render_template('api.html', rate_limit=LIND_RATE_LIMIT)

@api.route('/<lind_id>', methods=['GET','PUT'])
def api_lind_info(lind_id: str):
	data = request.args.to_dict()
	if request.method == 'GET':
		try:
			result = get_url(
				lind_id=lind_id,
				intention='manage',
				admin_password=data.get('admin_password', None)
			)
		except LindIdNotFound:
			return {'error': 'LindIdNotFound', 'result': {}}, 404
		except NotManageable:
			return {'error': 'NotManageable', 'result': {}}, 400
		except ManageUnauthorized:
			return {'error': 'ManageUnauthorized', 'result': {}}, 401

		return {'error': None, 'result': result}, 200

	elif request.method == 'PUT':
		try:
			update_data = request.get_json(force=True)
			#convert expiration time to epoch
			if update_data.get('expiration_time', '') != '':
				update_data['expiration_time'] = datetime.strptime(data['expiration_time'], '%Y-%m-%dT%H:%M').timestamp()
			result = edit_url(
				lind_id=lind_id,
				url=update_data.get('url'),
				expiration_time=update_data.get('expiration_time') or -1,
				limit_usage=update_data.get('limit_usage') or -1,
				access_password=update_data.get('access_password') or None,
				admin_password=update_data.get('admin_password') or None
			)
		except LindIdNotFound:
			return {'error': 'LindIdNotFound', 'result': {}}, 404
		except InvalidExpirationTime:
			return {'error': 'InvalidExpirationtime', 'result': {}}, 400
		except InvalidLimitUsage:
			return {'error': 'InvalidLimitUsage', 'result': {}}, 400
		return {'error': None, 'result': result}, 204
		
@api.route('/create', methods=['POST'])
def api_create():
	rate_limiter_result = rate_limiter(request.remote_addr)
	if rate_limiter_result[0] == 'DISAPPROVED':
		return {'error': 'RateLimitReached', 'timeout': rate_limiter_result[1], 'result': {}}, 429

	data = request.get_json(force=True)
	try:
		#convert expiration time to epoch
		if data.get('expiration_time','') != '':
			data['expiration_time'] = datetime.strptime(data['expiration_time'], '%Y-%m-%dT%H:%M').timestamp()
		result = register_url(
			url = data.get('url'),
			expiration_time = data.get('expiration_time') or -1,
			limit_usage = data.get('limit_usage') or -1,
			access_password = data.get('access_password') or None,
			admin_password = data.get('admin_password') or None
		)
		return {'error': None, 'result': {'lind': result}}, 201
	except InvalidExpirationTime:
		return {'error': 'InvalidExpirationTime', 'result': {}}, 400
	except InvalidLimitUsage:
		return {'error': 'InvalidLimitusage', 'result': {}}, 400
