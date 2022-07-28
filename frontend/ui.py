#-*- coding: utf-8 -*-

from backend.backend import edit_url, register_url, get_url, rate_limiter
from backend.custom_exceptions import *

from flask import Blueprint, render_template, request, redirect
from datetime import datetime

ui = Blueprint('ui',__name__)

#add pages
@ui.route('/', methods=['GET'])
def index():
	return render_template('index.html')

@ui.route('/create', methods=['GET','POST'])
def create():
	if request.method == 'GET':
		return render_template('create.html')
	elif request.method == 'POST':
		rate_limiter_result = rate_limiter(request.remote_addr)
		if rate_limiter_result[0] == 'DISAPPROVED':
			return {'error': 'RateLimitReached', 'timeout': rate_limiter_result[1], 'result': {}}, 429

		data = request.form.to_dict()
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
		except InvalidExpirationTime:
			return render_template('create.html', error=True)
		except InvalidLimitUsage:
			return render_template('create.html')

		return redirect(f'/{result}/show')

@ui.route('/<lind_id>/show', methods=['GET'])
def show(lind_id: str):
	return render_template('show.html', link=f'{request.url_root}{lind_id}')

@ui.route('/<lind_id>', methods=['GET','POST'])
def lead(lind_id: str):
	try:
		access_password = request.form.to_dict().get('access_password')
		result = get_url(
			lind_id=lind_id,
			intention='access',
			access_password=access_password
		)
	except LindIdNotFound:
		return render_template('not_found.html')
	except AccessUnauthorized:
		return render_template('enter_password.html')
	
	return redirect(result)
	
@ui.route('/<lind_id>/manage', methods=['GET','POST'])
def manage(lind_id: str):
	try:
		data = request.form.to_dict()
		#convert expiration time to epoch
		if data.get('expiration_time','') != '':
			data['expiration_time'] = datetime.strptime(data['expiration_time'], '%Y-%m-%dT%H:%M').timestamp()
		admin_password = data.get('admin_password',None)
		result = get_url(
			lind_id=lind_id,
			intention='manage',
			admin_password=admin_password
		)
	except LindIdNotFound:
		return render_template('not_found.html')
	except NotManageable:
		return render_template('not_manageable.html')
	except ManageUnauthorized:
		return render_template('enter_password_manage.html')

	if data.get('intention') == 'edit':
		try:
			edit_url(
				lind_id=lind_id,
				url=data.get('url'),
				expiration_time=data.get('expiration_time') or -1,
				limit_usage=data.get('limit_usage') or -1,
				access_password=data.get('access_password') or None,
				admin_password=data.get('admin_password') or None
			)
		except LindIdNotFound:
			return render_template('not_found.html')
		except InvalidExpirationTime:
			return render_template('manage.html', info=result, admin_password=admin_password, error=True)
		except InvalidLimitUsage:
			return render_template('manage.html', info=result, admin_password=admin_password)
		return redirect('/')
	else:
		return render_template('manage.html', info=result, admin_password=admin_password)
