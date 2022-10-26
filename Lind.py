#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os.path import dirname, join
from sys import version_info

from flask import Flask, render_template, request
from waitress import create_server

from backend.db import close_db, maintain_db, setup_db
from frontend.api import api
from frontend.ui import ui

HOST = "0.0.0.0"
PORT = "8080"
THREADS = 10

def _folder_path(*folders):
	return join(dirname(__file__), *folders)

def create_app() -> Flask:
	app = Flask(
		__name__,
		template_folder=_folder_path("frontend", "templates"),
		static_folder=_folder_path("frontend", "static"),
		static_url_path="/static"
	)
	app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True

	# add error handlers
	@app.errorhandler(404)
	def not_found(e):
		if request.path.startswith("/api"):
			return {"error": "NotFound", "result": {}}, 404
		else:
			return render_template("page_not_found.html")

	@app.errorhandler(400)
	def bad_request(e):
		return {"error": "Bad request", "result": {}}, 400

	@app.errorhandler(405)
	def method_not_allowed(e):
		return {"error": "Method not allowed", "result": {}}, 405

	@app.errorhandler(500)
	def internal_error(e):
		return {"error": "Internal error", "result": {}}, 500

	app.register_blueprint(ui)
	app.register_blueprint(api, url_prefix="/api")

	# setup database
	app.teardown_appcontext(close_db)

	return app

def Lind() -> None:
	# check python version
	if (version_info.major < 3) or (version_info.major == 3 and version_info.minor < 7):
		print(
			f"Error: the minimum python version required is python3.7 (currently {version_info.major}.{version_info.minor}.{version_info.micro})"
		)

	app = create_app()

	# setup database
	with app.app_context():
		setup_db()

	# create server instance
	server = create_server(app, host=HOST, port=PORT, threads=THREADS)

	# start application
	print(f"Lind running on http://{HOST}:{PORT}/")
	server.run()

	# shutdown application
	maintain_db().maintain()
	print("\nBye!")
	return

if __name__ == "__main__":
	Lind()
