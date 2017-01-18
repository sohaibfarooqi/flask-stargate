from flask import request, Flask, current_app
from .request import RequestCls
from .response import ResponseCls
from .setting import ApplicationSettings

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
	request_class = RequestCls
	response_class = ResponseCls


	def __init__(self, app_url_prefix = None, *args, **kwargs):
		"""Application constructor registering application setting and initilizing Flask app. 
		"""
		super(Application, self).__init__(*args, **kwargs)
		self.api_settings = ApplicationSettings(self.config)
		self.blueprints = []#hold reference to current_app's blueprints
		#default url prefix for app context.
		if app_url_prefix is not None:
			bp = Blueprint(str(uuid1()), __name__, url_prefix = app_url_prefix)
			self.register_blueprint(bp)

	def preprocess_request(self):
		"""Method overriden from Flask to perform any application specific preprocessing. 
		"""
		pass

	def register_resource_as_api(self, *args, **kwargs):
		"""Register callable endpoints for a particular resource.
		"""	
		blueprint_name = str(uuid1())
        blueprint = ResourceManager.create_api_blueprint(blueprint_name, *args, **kw)
        self.blueprints.append(blueprint)

        if app is not None:
            app.register_blueprint(blueprint)

	def make_response(self, rv):
		"""Method overriden from Flask to perform any application specific postprocessing. 
		"""
		pass

	def handle_user_exception(self, e):
		"""Method overriden from Flask to format error in Application specific format. 
		"""
		pass

	def handle_api_exception(self, exc):
		"""Method to handle Api Exception. 
		"""
		pass