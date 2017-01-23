from flask import Flask
from .response_cls import ResponseCls

class Application(Flask):
	"""Main Application class for initilizing Flask app. It handles Application Setting. It also overrides request and response classes according to 
	application specs.
	
	Usage:
		>>> from core_api_v3 import Application
		>>> app = Application(__name__)

	"""
	#Application Version
	__VERSION__ = '0.1.0'

	#Apopted from => http://flask.pocoo.org/docs/0.12/patterns/subclassing/
	response_class = ResponseCls