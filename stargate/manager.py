"""Main class exposed to users. This class manages model registration as endpoints. It wraps all view/db actions. 
For details about this class check docs. Supported options for api_endpoints can be found in `create_resource_blueprint` method

"""

from flask import Flask, Blueprint, url_for, json, make_response
from uuid import uuid1
from collections import namedtuple
from .proxy import manager_info
from .serializer import Serializer
from .deserializer import Deserializer
from functools import partial
from .exception import IllegalArgumentError, StargateException
from werkzeug.exceptions import HTTPException
from .resource_api import ResourceAPI
from flask.testing import FlaskClient
from sqlalchemy.inspection import inspect as sqlalchemy_inspect
from sqlalchemy.exc import NoInspectionAvailable
from .const import ResourceConst

#HTTP Method for fetching resource/collection
READONLY_METHODS = frozenset(('GET', ))
#HTTP Methods for modifying resources
WRITEONLY_METHODS = frozenset(('PATCH', 'POST', 'DELETE',))
#Set containing all available HTTP Methods
ALL_METHODS = READONLY_METHODS | WRITEONLY_METHODS
#Default `url_prefix` for `Manager` Class
DEFAULT_URL_PREFIX = '/api'
#Namedtuple to hold information about a resource registered with a `Manager` instance
RESOURCE_INFO = namedtuple('RESOURCE_INFO', ['collection','blueprint','serializer','deserializer', 'pk','apiname'])

class Manager():
	"""This class let you expose JSON RESTFul APIs against various resources.
	
	``app`` should be :class:`~flask.Flask` instance. If you wish to use `flask test client`
	for testing you can also provide :class:`~flask.Flask.FlaskClient` instance. 
	
	``db`` should be :class:`~flask_sqlalchemy.SQLAlchemy` instance.
	
	``decorators`` should be python decorators. Each resource registered with a manager
	instance will invoke all specified decorators before view functions are invoked.

	``url_prefix`` prefix url for all endpoints registered with `Manager` instance. url_prefix
	should start with '/'.
	
	Example usage of this class. Models should be defined using flask_sqlalchemy:

	.. sourcecode:: python
		
		from stargate import Manager
		from models import User

		manager = Manager(app, db)
		#With decorators
		manager = Manager(app, db, decorators = [auth_decorator])
		#With url_prefix
		manager = Manager(app, db, url_prefix = '/v1')
	
	"""	
	def __init__(self, app, db, decorators = None, url_prefix = None):

		if isinstance(app, Flask):
			self.app = app
			self.register_exception_handler(app)
		
		elif isinstance(app, FlaskClient):
			self.app = app
		
		else:
			msg = "Provided app instance should be `flask.Flask` or `flask.Flask.FlaskClient` instance instead of %s" %str(type(app))
			raise ValueError(msg)

		manager_info.register(self)

		self.session = db.session
		self.url_prefix = url_prefix
		
		self.decorators = decorators or []
		self.registered_apis = {}
		self.registerd_blueprints = []

	@staticmethod
	def api_name(collection_name):
		return "{0}api".format(collection_name)

	def register_resource(self, *args, **kwargs):
		"""This method perform sanity check of argument passed, create resource blueprint
		blueprint, register it with :class:`~flask.Flask` and finally add this blueprint to registered blueprints
		
		Example usage of this method

		.. sourcecode:: python
		
			from stargate import Manager
			from models import User

			manager = Manager(app, db)
			manager.register_resource(User)

		This method supports sereral options:
			
		.. sourcecode:: python
		
			from stargate import Manager
			from models import User

			manager = Manager(app, db)
			
			#Specify resource methods
			manager.register_resource(User, methods = ['GET', 'POST'])
			
			#Specify url_prefix
			manager.register_resource(User, url_prefix = '/v2')
			
			#Specify endpoint
			manager.register_resource(User, endpoint = '/onlineusers')
			
			#Specify resource fields
			manager.register_resource(User, fields = ['username', 'email', 'date_added'])
			
			#Exclude resource attributes
			manager.register_resource(User, exclude = ['password'])
			
			#Specify resource decorators
			manager.register_resource(User, decorators = [check_user_quota])
			
			#Specify resource primary key
			manager.register_resource(User, primary_key = 'ser_id')

		"""
		blueprint_name = str(uuid1())

		if self._args_sanity_checks(blueprint_name, *args, **kwargs):
			blueprint = self.create_resource_blueprint(blueprint_name, *args, **kwargs)
			self.registerd_blueprints.append(blueprint)

		if self.app is not None:
			self.app.register_blueprint(blueprint)

		else:
			msg = "`Flask App` not initilized"
			raise RuntimeError(msg)
	
	def create_resource_blueprint(self, name, model, methods = READONLY_METHODS,
                             url_prefix = None, endpoint = None,fields = None, 
                       		exclude = None, decorators = [], primary_key = None):
		"""This method returns blueprint of a resource with specified options.

		``name``: blueprint name

		``model``: user defined model class Using :class:`~flask_sqlalchemy.SQLALchemy.Model` 
		
		``methods``: HTTP methods allowed on resource 
		
		``url_prefix``: prefix url for specific resource 
		
		``endpoint``: resource endpoint. By default it would be ``table.__name__``. 
		
		``fields``: allowed fields for Serializer. 
		
		``exclude``: exclude fields for Serializer. 
		
		``decorators``: view decorator functions. 
		
		``primary_key``: primary key column. By default `id` will be used

		This method register view functions using :class:`~stargate.resource_api.ResourceAPI`
		and provide `endpoint`, `session`, `model` and `primary key`. It also register endpoint
		using :meth:`~flask.Flask.Blueprint.add_url_rule`. Collection and instances have different 
		HTTP methods and url schemes. Finally this method populate the namedtuple ``RESOURCE_INFO`` 

		"""
		if endpoint is None:
			endpoint = model.__table__.name
		
		methods = frozenset((m.upper() for m in methods))
		apiname = self.api_name(endpoint)

		decorators_ = self.decorators
		decorators_.extend(decorators)

		if primary_key is None:
			if hasattr(model, ResourceConst.PRIMARY_KEY_COLUMN):
				primary_key = ResourceConst.PRIMARY_KEY_COLUMN  
			else: 
				raise ValueError("Model {0} has no specified primary_key".format(model.__class__))
		
		serializer = Serializer(model, primary_key, fields=fields, exclude=exclude)

		deserializer = Deserializer(model, self.session)

		resource_api_view = ResourceAPI.as_view( apiname, self.session, model, primary_key)

		for decorator in decorators_:
			resource_api_view = decorator(resource_api_view)

		if url_prefix is not None:
			prefix = url_prefix
		elif self.url_prefix is not None:
			prefix = self.url_prefix
		else:
			prefix = DEFAULT_URL_PREFIX

		blueprint = Blueprint(name, __name__, url_prefix=prefix)
		#TODO: Segregate collection and resource methods
		collection_url = '/{0}'.format(endpoint)
		collection_methods = ALL_METHODS & methods
		self._add_endpoint(blueprint, collection_url, resource_api_view, methods=collection_methods)
		
		resource_url = '/{0}/<pk_id>'.format(endpoint)
		resource_methods = ALL_METHODS & methods
		self._add_endpoint(blueprint, resource_url, resource_api_view ,methods=resource_methods)
		
		nested_collection_url = '{0}/<relation>'.format(resource_url)
		self._add_endpoint(blueprint, nested_collection_url, resource_api_view ,methods=resource_methods)
		
		nested_instance_url = '{0}/<related_id>'.format(nested_collection_url)
		self._add_endpoint(blueprint, nested_instance_url, resource_api_view ,methods=resource_methods)

		self.registered_apis[model] = RESOURCE_INFO(endpoint, blueprint.name, serializer, deserializer, primary_key, apiname)

		return blueprint		

	def _add_endpoint(self, blueprint, endpoint, view_func, methods=READONLY_METHODS):
		"""Add url rule by invoking `flask.Flask.Blueprint.add_url_rule` method. Provides
		view function and HTTP methods to add_rule.
		"""
		add_rule = blueprint.add_url_rule
		add_rule(endpoint, view_func=view_func, methods=methods)

	def register_exception_handler(self, app):
		"""Register application exception handler and user exception handler. use
		:meth:`~Manager._exception_handler` class method and check if thrown exception 
		is of :class:`~stargate.exception.StargateException` or 
		:class:`~werkzeug.exceptions.HTTPException`

		"""
		app.handle_exception = partial(self._exception_handler, app.handle_exception)
		app.handle_user_exception = partial(self._exception_handler, app.handle_user_exception)
	
	def _exception_handler(self, original_handler, e):
		"""Return :meth:`~stargate.exception.StargateException.get_response` for application errors
		or in case of werkzeug exceptions(MethodNotAllowed, ResourceNotFound) it returns
		:meth:`~Manager._make_response`.

		"""
		if isinstance(e, StargateException):
			return e.get_response()

		elif isinstance(e, HTTPException):
			return self._make_response({'status': e.code,'message': e.description}, e.code)

		return original_handler(e)

	def _make_response(self, data, code, headers=None):
		"""This method is internally used in class in case of 
		:class:`~werkzeug.exceptions.HTTPException` raised in application.

		"""
		settings = {}
		settings.setdefault('indent', 4)
		settings.setdefault('sort_keys', True)

		data = json.dumps(data, **settings)

		resp = make_response(data, code)
		resp.headers.extend(headers or {})
		return resp

	def _args_sanity_checks(self, name, model, methods = None,
                             url_prefix = None, endpoint = None,fields = None, 
                             validation_exceptions = (), exclude = None, 
                             decorators = [], primary_key = None):

		"""This method is invoked from :meth:`~Manager.register_resource` to perform 
		sanity checks on the values provided. Raises :class:`~stargate.exceptions.IllegalArgumentError`
		with appropriate message.

		"""
		if fields is not None and exclude is not None:
			msg = 'Cannot simultaneously specify both `fields` and `exclude` for model {0}'
			raise IllegalArgumentError(msg.format(model.__name__))

		if primary_key is None and not hasattr(model, ResourceConst.PRIMARY_KEY_COLUMN):
			msg = 'Provided model is missing `id` attribute and no default primary key provided model {0}'
			raise IllegalArgumentError(msg.format(model.__name__))

		if endpoint == '':
			msg = 'Collection name must be nonempty for model {0}'
			raise IllegalArgumentError(msg.format(model.__name__))

		if name in self.registerd_blueprints:
			msg = 'Duplicate Blueprint hash'
			raise IllegalArgumentError("{0}: Error {1}".format(name, msg))
		
		try:
			instance = sqlalchemy_inspect(model)
		except NoInspectionAvailable as e:
			msg = "No Inspection available for model {0}"
			raise IllegalArgumentError(msg.format(model.__name__))
		
		if url_prefix is not None and not url_prefix.startswith('/'):
			msg = "Malformed url_prefix for model {0}, prefix {1}"
			raise IllegalArgumentError(msg.format(model.__name__, url_prefix))
		
		if methods is not None and not all(meth in ALL_METHODS for meth in methods):
			msg = "Invalid HTTP method in list {0} for model {1}"
			raise IllegalArgumentError(msg.format(methods, model.__name__)) 
		
		for decorator in decorators:
			if not callable(decorator):
				msg = "Decorator should be callable model {0} decorator {1}"
				raise IllegalArgumentError(msg.format(model.__name__, decorator))
		
		return True