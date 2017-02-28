import inspect
from flask import Flask, Blueprint, url_for, json, make_response
from six import string_types
from uuid import uuid1
from collections import namedtuple, defaultdict
from .proxy import manager_info
from .serializer import Serializer
from .deserializer import Deserializer
from functools import partial
from .exception import IllegalArgumentError, StargateException
from werkzeug.exceptions import HTTPException
from .views import ResourceAPI
from flask.testing import FlaskClient

READONLY_METHODS = frozenset(('GET', ))
WRITEONLY_METHODS = frozenset(('PATCH', 'POST', 'DELETE',))
ALL_METHODS = READONLY_METHODS | WRITEONLY_METHODS
DEFAULT_URL_PREFIX = '/api'
RESOURCE_INFO = namedtuple('RESOURCE_INFO', ['collection','blueprint','serializer','deserializer', 'pk','apiname'])
DEFAULT_PRIMARY_KEY_COLUMN = 'id'

class ResourceManager():
	
	def __init__(self, app, db, _decorators = None, url_prefix = None):

		if isinstance(app, Flask):
			self.app = app
			self.register_exception_handler(app)
		
		elif isinstance(app, FlaskClient):
			self.app = app
		
		else:
			msg = "Provided app instance should be `Flask` or `FlaskClient` instance instead of %s" %str(type(app))
			raise IllegalArgumentError(msg)

		manager_info.register(self)

		self.session = db.session
		self.url_prefix = url_prefix
		
		self.decorators = _decorators or []
		self.registerd_blueprints = []
		self.registered_apis = {}

	@staticmethod
	def api_name(collection_name):
		return "{0}api".format(collection_name)

	def register_resource(self, *args, **kwargs):
    
		blueprint_name = str(uuid1())
		blueprint = self.create_resource_blueprint(blueprint_name, *args, **kwargs)
		self.registerd_blueprints.append(blueprint)

		if self.app is not None:
			self.app.register_blueprint(blueprint)

		else:
			msg = "`Flask App` not initilized"
			raise RuntimeError(msg)
	
	def create_resource_blueprint(self, name, model, methods = READONLY_METHODS,
                             url_prefix = None, collection_name = None,fields = None, 
                             validation_exceptions = (),exclude = None, 
                             decorators = [], primary_key = None):
		
		if collection_name is None or collection_name == '':
			collection_name = model.__table__.name
		
		methods = frozenset((m.upper() for m in methods))
		apiname = self.api_name(collection_name)

		decorators_ = self.decorators
		decorators_.extend(decorators)

		if primary_key is None:
			if hasattr(model, DEFAULT_PRIMARY_KEY_COLUMN):
				primary_key = DEFAULT_PRIMARY_KEY_COLUMN  
			else: 
				raise ValueError("Model {0} has no specified primary_key".format(model.__class__))
		
		serializer = Serializer(model, primary_key, fields=fields, exclude=exclude)

		deserializer = Deserializer(model, self.session)

		resource_api_view = ResourceAPI.as_view( apiname, self.session, model, validation_exceptions, primary_key)

		for decorator in decorators_:
			resource_api_view = decorator(resource_api_view)

		if url_prefix is not None:
			prefix = url_prefix
		elif self.url_prefix is not None:
			prefix = self.url_prefix
		else:
			prefix = DEFAULT_URL_PREFIX

		blueprint = Blueprint(name, __name__, url_prefix=prefix)
		#Segregate collection and resource methods
		collection_url = '/{0}'.format(collection_name)
		collection_methods = ALL_METHODS & methods
		self._add_endpoint(blueprint, collection_url, resource_api_view, methods=collection_methods)
		
		resource_url = '/{0}/<pk_id>'.format(collection_name)
		resource_methods = ALL_METHODS & methods
		self._add_endpoint(blueprint, resource_url, resource_api_view ,methods=resource_methods)
		
		nested_collection_url = '{0}/<relation>'.format(resource_url)
		self._add_endpoint(blueprint, nested_collection_url, resource_api_view ,methods=resource_methods)
		
		nested_instance_url = '{0}/<related_id>'.format(nested_collection_url)
		self._add_endpoint(blueprint, nested_instance_url, resource_api_view ,methods=resource_methods)

		self._add_resource(model, collection_name, blueprint, serializer, deserializer, primary_key, apiname)

		return blueprint

	def _add_resource(self, model, collection_name, blueprint, serializer, deserializer, primary_key, apiname):
		self.registered_apis[model] = RESOURCE_INFO(collection_name, blueprint.name, serializer, deserializer, primary_key, apiname)

	def _add_endpoint(self, blueprint, endpoint, view_func, methods=READONLY_METHODS):
		add_rule = blueprint.add_url_rule
		add_rule(endpoint, view_func=view_func,
					methods=methods)

	def register_exception_handler(self, app):
		app.handle_exception = partial(self._exception_handler, app.handle_exception)
		app.handle_user_exception = partial(self._exception_handler, app.handle_user_exception)
	
	def _exception_handler(self, original_handler, e):
		if isinstance(e, StargateException):
			return e.get_response()

		elif isinstance(e, HTTPException):
			return self._make_response({'status': e.code,'message': e.description}, e.code)

		return original_handler(e)

	def _make_response(self, data, code, headers=None):
    	
		settings = {}
		settings.setdefault('indent', 4)
		settings.setdefault('sort_keys', True)

		data = json.dumps(data, **settings)

		resp = make_response(data, code)
		resp.headers.extend(headers or {})
		return resp

	def _args_sanity_checks(self, *args, **kwargs):

		if fields is not None and exclude is not None:
			msg = 'Cannot simultaneously specify both `only` and `exclude`'
			raise IllegalArgumentError(msg)

		if not hasattr(model, 'id'):
			msg = 'Provided model must have an `id` attribute'
			raise IllegalArgumentError(msg)

		if collection_name == '':
			msg = 'Collection name must be nonempty'
			raise IllegalArgumentError(msg)

		return True