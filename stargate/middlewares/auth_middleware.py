from flask import jsonify
import json

class AuthMiddleware():

	def __init__(self, app):
		self.app = app

	def __call__(self, environ, start_response):
		if self._authenticated(environ.get('HTTP_AUTHORIZATION')):
			return self.app(environ, start_response)
		else:
			return self._login(environ, start_response)

	def _authenticated(self, header):
		return True

	def _login(self, environ, start_response):
		start_response('401 Authentication Required',
			[('Content-Type', 'application/json'),
			('WWW-Authenticate', 'Basic realm="Login"')])
		return self.app(environ, start_response)