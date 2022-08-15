#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from frontend.ui import ui
from frontend.api import api
from backend.backend import startup, database_maintenance

from sys import version_info
from flask import Flask, render_template, request
from waitress.server import create_server
from os.path import join, dirname

HOST = '0.0.0.0'
PORT = '8080'
THREADS = 100

def _folder_path(*folders):
	return join(dirname(__file__), *folders)

def Lind():
	#check python version
	if (version_info.major < 3) or (version_info.major == 3 and version_info.minor < 7):
		print(f'Error: the minimum python version required is python3.7 (currently {version_info.major}.{version_info.minor}.{version_info.micro})')

	#register web server
	app = Flask(
		__name__,
		template_folder=_folder_path('frontend','templates'),
		static_folder=_folder_path('frontend','static'),
		static_url_path='/static'
	)
	app.config['SECRET_KEY'] = 'thisisaverysecretkey'
	app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

	#add error handlers
	@app.errorhandler(404)
	def not_found(e):
		if request.path.startswith('/api'):
			return {'error': 'Not Found', 'result': {}}, 404
		else:
			return render_template('page_not_found.html')
	
	@app.errorhandler(400)
	def bad_request(e):
		return {'error': 'Bad request', 'result': {}}, 400

	@app.errorhandler(405)
	def method_not_allowed(e):
		return {'error': 'Method not allowed', 'result': {}}, 405

	@app.errorhandler(500)
	def internal_error(e):
		return {'error': 'Internal error', 'result': {}}, 500

	app.register_blueprint(ui)
	app.register_blueprint(api, url_prefix="/api")

	#setup database
	startup()

	#create waitress server	and run
	server = create_server(app, host=HOST, port=PORT, threads=THREADS)
	print(f'Lind running on http://{HOST}:{PORT}/')
	server.run()
	
	#save after server stops
	database_maintenance(full=True)
	print('\nBye')

if __name__ == "__main__":
	Lind()
