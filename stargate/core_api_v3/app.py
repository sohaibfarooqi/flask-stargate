from flask import Flask
from .response_cls import ResponseCls
from werkzeug.exceptions import HTTPException

class Application(Flask):
	"""Main Application class for initilizing Flask app. It handles Application Setting. It also overrides request and response classes according to 
	application specs.
	
	Usage:
		>>> from core_api_v3 import Application
		>>> app = Application(__name__)

	"""
	#Apopted from => http://flask.pocoo.org/docs/0.12/patterns/subclassing/
	response_class = ResponseCls

	def handle_user_exception(self, e):
		exc_type, exc_value, tb = sys.exc_info()
        assert exc_value is e

        if isinstance(e, HTTPException) and not self.trap_http_exception(e):
            return self.handle_http_exception(e)

        if isinstance(e, AppException):
            return self.handle_app_exception(e)

        blueprint_handlers = ()
        handlers = self.error_handler_spec.get(request.blueprint)
        if handlers is not None:
            blueprint_handlers = handlers.get(None, ())
        app_handlers = self.error_handler_spec[None].get(None, ())
        if is_flask_legacy():
            for typecheck, handler in chain(blueprint_handlers, app_handlers):
                if isinstance(e, typecheck):
                    return handler(e)
        else:
            for typecheck, handler in chain(dict(blueprint_handlers).items(),
                    dict(app_handlers).items()):
                if isinstance(e, typecheck):
                    return handler(e)

        reraise(exc_type, exc_value, tb)

	def handle_app_exception(self, exc):
		return ResponseCls({'message': exc.detail}, status = exc.status_code)
