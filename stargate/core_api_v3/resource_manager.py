from flask import Flask, Blueprint, url_for as flask_url_for
from six import string_types
from uuid import uuid1
from collections import namedtuple, defaultdict
from .broker import url_for, serializer_for, primary_key_for, collection_name_for, model_for
from .serializer import DefaultSerializer
from .deserializer import DefaultDeserializer
from .views.collection import CollectionAPI

READONLY_METHODS = frozenset(('GET', ))
WRITEONLY_METHODS = frozenset(('PATCH', 'POST', 'DELETE'))
ALL_METHODS = READONLY_METHODS | WRITEONLY_METHODS
DEFAULT_URL_PREFIX = '/api'
RESOURCE_API_INFO = namedtuple('RESOURCE_API_INFO', ['collection', 
                                                    'blueprint', 
                                                    'serializer',
                                                    'deserializer',
                                                    'pk'])
class ResourceManager():
	
	APINAME_FORMAT = '{0}api'

	def __init__(self, app, sqlalchemy_session = None, flask_sqlalchemy_db = None,
				preprocessors = None, postprocessors = None, url_prefix = None):

		if isinstance(app, Flask):
			self.app = app
			self.init_app(app)
		else:
			msg = "Provided app instance should be `Flask` instance instead of %s" %str(type(app));
			raise IllegalArgumentError(msg)

		if sqlalchemy_session is not None:
			self.session = sqlalchemy_session
		elif flask_sqlalchemy_db is not None:
			self.session = flask_sqlalchemy_db.session
		else:
			msg = 'must specify either `flask_sqlalchemy_db` or `sqlalchemy_session`'
			raise IllegalArgumentError(msg)

		self.pre = preprocessors or {}
		self.post = postprocessors or {}

		self.registerd_blueprints = []

		self.registered_apis = {}

		self.url_prefix = url_prefix

		url_for.register(self)
		serializer_for.register(self)
		primary_key_for.register(self)
		model_for.register(self)
		collection_name.register(self)

	@staticmethod
	def api_name(collection_name):
		return ResourceManager.APINAME_FORMAT.format(collection_name)

	def register_resource(self, *args, **kwargs):
    
		blueprint_name = str(uuid1())
		blueprint = self.create_resource_blueprint(blueprint_name, *args, **kwargs)
		self.registerd_blueprints.append(blueprint)

		if self.app is not None:
			self.app.register_blueprint(blueprint)

		else:
			msg = "Application not initilized"
			raise RuntimeError(msg)

	def init_app(self, app):
		app.handle_exception = partial(self._exception_handler, app.handle_exception)
		app.handle_user_exception = partial(self._exception_handler, app.handle_user_exception)
	
	def add_resource():
		pass
	
	def add_route():
		pass
	
	def add_view():
		pass
	
	def _exception_handler(self, original_handler, e):
        if isinstance(e, ApplicationException):
            return e.get_response()

        if not request.path.startswith(self.prefix):
            return original_handler(e)

        if isinstance(e, HTTPException):
            return _make_response({
                'status': e.code,
                'message': e.description
            }, e.code)

		return original_handler(e)
	def create_resource_blueprint(self, name, model, methods=READONLY_METHODS,
                             url_prefix=None, collection_name=None,
                             allow_functions=False, only=None, exclude=None,
                             additional_attributes=None,
                             validation_exceptions=None, page_size=10,
                             max_page_size=100, decorators=[], primary_key=None,
                             serializer=None, deserializer=None,
                             includes=None, allow_to_many_replacement=False,
                             allow_delete_from_to_many_relationships=False,
                             allow_client_generated_ids=False):
		
		if collection_name is None:
			collection_name = model.__table__.name
		methods = frozenset((m.upper() for m in methods))
		apiname = ResourceManager.api_name(collection_name)

		decorators_ = self.decorators
		decorators_.append(decorators)
		
		if serializer is None:
			serializer = DefaultSerializer(only, exclude,
											additional_attributes)

		if deserializer is None:
			deserializer = DefaultDeserializer(self.session, model,
												allow_client_generated_ids)

		atmr = allow_to_many_replacement
		api_view = CollectionAPI.as_view(apiname, 
										self.session, 
										model,
										decorators = decorators_,
										primary_key = primary_key,
										validation_exceptions = validation_exceptions,
										allow_to_many_replacement = atmr,
										page_size = page_size,
										max_page_size = max_page_size,
										serializer = serializer,
										deserializer = deserializer,
										includes = includes)

		if url_prefix is not None:
			prefix = url_prefix
		elif self.url_prefix is not None:
			prefix = self.url_prefix
		else:
			prefix = DEFAULT_URL_PREFIX
			blueprint = Blueprint(name, __name__, url_prefix=prefix)
			add_rule = blueprint.add_url_rule

		collection_url = '/{0}'.format(collection_name) #/users
		# resource_url = '{0}/<resource_id>'.format(collection_url) #/users/1
		# related_resource_url = '{0}/<relation_name>'.format(resource_url) #/users/1/userdetails
		# to_many_resource_url = '{0}/<related_resource_id>'.format(related_resource_url) #/users/1/userdetails/2
		# relationship_url = '{0}/relationships/<relation_name>'.format(resource_url) #/users/1/userdetails/relationships/secret_key


		# relationship_api_name = '{0}.relationships'.format(apiname)
		# rapi_view = RelationshipAPI.as_view
		# adftmr = allow_delete_from_to_many_relationships
		# relationship_api_view = rapi_view(relationship_api_name, session, model,
		# preprocessors=preprocessors_,
		# postprocessors=postprocessors_,
		# primary_key=primary_key,
		# validation_exceptions=validation_exceptions,
		# allow_to_many_replacement=allow_to_many_replacement,
		# allow_delete_from_to_many_relationships=adftmr)

		# relationship_methods = READONLY_METHODS & methods
		# if 'PATCH' in methods:
		#     relationship_methods |= WRITEONLY_METHODS
		# add_rule(relationship_url, methods=relationship_methods,
		#          view_func=relationship_api_view)

		collection_methods = frozenset(('POST', )) & methods
		add_rule(collection_url, view_func=api_view,
					methods=collection_methods)
		collection_methods = frozenset(('GET', )) & methods
		add_rule(collection_url, view_func=api_view,
					methods=collection_methods)

		# resource_methods = frozenset(('DELETE', 'PATCH')) & methods
		# add_rule(resource_url, view_func=api_view, methods=resource_methods)
		# resource_methods = READONLY_METHODS & methods
		# resource_defaults = dict(relation_name=None, related_resource_id=None)
		# add_rule(resource_url, view_func=api_view, methods=resource_methods,
		#          defaults=resource_defaults)

		# related_resource_methods = READONLY_METHODS & methods
		# related_resource_defaults = dict(related_resource_id=None)
		# add_rule(related_resource_url, view_func=api_view,
		#          methods=related_resource_methods,
		#          defaults=related_resource_defaults)

		# to_many_resource_methods = READONLY_METHODS & methods
		# add_rule(to_many_resource_url, view_func=api_view,
		#          methods=to_many_resource_methods)

		# if allow_functions:
		#     eval_api_name = '{0}.eval'.format(apiname)
		#     eval_api_view = FunctionAPI.as_view(eval_api_name, session, model)
		#     eval_endpoint = '/eval{0}'.format(collection_url)
		#     eval_methods = ['GET']
		#     blueprint.add_url_rule(eval_endpoint, methods=eval_methods,
		#                            view_func=eval_api_view)

		self.registered_apis[model] = RESOURCE_API_INFO(collection_name, blueprint.name,
												serializer, deserializer, primary_key)
		return blueprint

	def url_for(self, model, **kw):
		collection_name = self.registered_apis[model].collection
		blueprint_name = self.registered_apis[model].blueprint
		api_name = ResourceManager.api_name(collection_name)
		parts = [blueprint_name, api_name]
		url = flask_url_for('.'.join(parts), **kw)
		return url

	def collection_name(self, model):
		return self.registered_apis[model].collection

	def serializer_for(self, model):
		return self.registered_apis[model].serializer

	def primary_key_for(self, model):
		return self.registered_apis[model].pk

	def _params_sanity_checks(self, *args, **kwargs):

		if only is not None and exclude is not None:
			msg = 'Cannot simultaneously specify both `only` and `exclude`'
			raise IllegalArgumentError(msg)

		if not hasattr(model, 'id'):
			msg = 'Provided model must have an `id` attribute'
			raise IllegalArgumentError(msg)

		if collection_name == '':
			msg = 'Collection name must be nonempty'
			raise IllegalArgumentError(msg)

		if page_size < 0:
			msg = 'Page Size must be a positive integer'
			raise IllegalArgumentError(msg)

		if max_page_size < 0 or max_page_size > 100:
			msg = 'Max Page Size must be a positive integer and less then 100'
			raise IllegalArgumentError(msg)

		if additional_attributes is not None:
			for attr in additional_attributes:
				if isinstance(attr, string_types) and not hasattr(model, attr):
					msg = 'no attribute named: "{0}" found in Model: {1}'.format(attr, model)
					raise AttributeError(msg)
		return True
    