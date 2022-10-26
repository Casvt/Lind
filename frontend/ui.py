# -*- coding: utf-8 -*-

from flask import Blueprint, redirect, render_template, request
from backend.custom_exceptions import (
	AccessUnauthorized,
	LindNotFound,
	NotManageable,
)
from backend.lind import Lind

ui = Blueprint("ui", __name__)

methods = ["GET"]

@ui.route("/", methods=methods)
def ui_index():
	return render_template("index.html")

@ui.route("/<lind_id>", methods=methods)
def ui_redirect(lind_id: str):
	access_password = request.values.get("access_password")
	try:
		lind = Lind(lind_id, access_password=access_password)
		url = dict(lind)['url']

	except LindNotFound:
		return render_template("lind_not_found.html")
	except AccessUnauthorized:
		return render_template("enter_password_access.html")

	else:
		return redirect(url)

@ui.route('/<lind_id>/show', methods=methods)
def ui_show(lind_id: str):
	try:
		Lind(lind_id)
	except LindNotFound:
		return render_template('lind_not_found.html')

	except AccessUnauthorized:
		return render_template('show_lind.html')
	else:
		return render_template('show_lind.html')

@ui.route("/<lind_id>/manage", methods=methods)
def ui_manage(lind_id: str):
	try:
		lind = Lind(lind_id, admin_password="")

	except LindNotFound:
		return render_template("lind_not_found.html")
	except NotManageable:
		return render_template("not_manageable.html")
	except AccessUnauthorized:
		return render_template("manage_lind.html")

@ui.route('/use', methods=methods)
def ui_use():
	return render_template('use_lind.html')

@ui.route('/manage', methods=methods)
def ui_manage_page():
	return render_template('manage.html')

@ui.route("/api-docs", methods=methods)
def ui_docs():
	return render_template("api.html")

@ui.route("/create", methods=methods)
def ui_create():
	return render_template("create.html")
