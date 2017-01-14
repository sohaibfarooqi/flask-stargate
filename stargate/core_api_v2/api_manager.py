from collections import defaultdict
from collections import namedtuple
from uuid import uuid1
from flask import Blueprint
from flask import url_for as flask_url_for
import sys

READONLY_METHODS = frozenset(('GET', ))

WRITEONLY_METHODS = frozenset(('PATCH', 'POST', 'DELETE'))

ALL_METHODS = READONLY_METHODS | WRITEONLY_METHODS

DEFAULT_URL_PREFIX = '/api'

STRING_TYPES = (str, unicode)

APIInfo = namedtuple('APIInfo', ['collection_name', 'blueprint_name', 'serializer',
                                 'primary_key'])


class IllegalArgumentError(Exception):
    pass

class APIManager():

	APINAME_FORMAT = '{0}api'

	def __init__(self, app, flask_sqlalchemy_db = None, sqlalchemy_session = None, 
				preprocessors = None, postprocessors = None, url_prefix = None):
		
		if flask_sqlalchemy_db is None and sqlalchemy_session is None:
			msg = 'must specify either `flask_sqlalchemy_db` or `sqlalchemy_session`'
			raise ValueError(msg)

		self.app = app

		url_for.register(self)
        model_for.register(self)
        collection_name.register(self)
        serializer_for.register(self)
        primary_key_for.register(self)

		self.created_apis_for = {}

        self.blueprints = []

        if flask_sqlalchemy_db is not None:
            session = flask_sqlalchemy_db.session

        self.pre = preprocessors or {}
        self.post = postprocessors or {}
        self.session = sqlalchemy_session

        self.url_prefix = url_prefix


	@staticmethod
    def api_name(collection_name):
        
        return APIManager.APINAME_FORMAT.format(collection_name)

	def create_api(self, *args, **kwargs):
		
		blueprint_name = str(uuid1())
        blueprint = self.create_api_blueprint(blueprint_name, *args, **kw)
        self.blueprints.append(blueprint)

        if self.app is not None:
            self.app.register_blueprint(blueprint)

    def create_api_blueprint(self, name, model, methods=READONLY_METHODS,
                             url_prefix=None, collection_name=None,
                             allow_functions=False, only=None, exclude=None,
                             additional_attributes=None,
                             validation_exceptions=None, page_size=10,
                             max_page_size=100, preprocessors=None,
                             postprocessors=None, primary_key=None,
                             serializer=None, deserializer=None,
                             includes=None, allow_to_many_replacement=False,
                             allow_delete_from_to_many_relationships=False,
                             allow_client_generated_ids=False):


    	if only is not None and exclude is not None:
            msg = 'Cannot simultaneously specify both `only` and `exclude`'
            raise IllegalArgumentError(msg)
        if not hasattr(model, 'id'):
            msg = 'Provided model must have an `id` attribute'
            raise IllegalArgumentError(msg)
        if collection_name == '':
            msg = 'Collection name must be nonempty'
            raise IllegalArgumentError(msg)
        if collection_name is None:
            collection_name = model.__table__.name
        
        methods = frozenset((m.upper() for m in methods))
        apiname = APIManager.api_name(collection_name)
        preprocessors_ = defaultdict(list)
        postprocessors_ = defaultdict(list)
        preprocessors_.update(preprocessors or {})
        postprocessors_.update(postprocessors or {})
        for key, value in self.pre.items():
            preprocessors_[key] = value + preprocessors_[key]
        for key, value in self.post.items():
            postprocessors_[key] = value + postprocessors_[key]
        if additional_attributes is not None:
            for attr in additional_attributes:
                if isinstance(attr, STRING_TYPES) and not hasattr(model, attr):
                    msg = 'no attribute "{0}" on model {1}'.format(attr, model)
                    raise AttributeError(msg)
        
        if serializer is None:
            serializer = DefaultSerializer(only, exclude,
                                           additional_attributes)
        
        session = self.session
        if deserializer is None:
            deserializer = DefaultDeserializer(self.session, model,
                                               allow_client_generated_ids)
        
        atmr = allow_to_many_replacement
        api_view = API.as_view(apiname, session, model,
        					   preprocessors=preprocessors_,
                               postprocessors=postprocessors_,
                               primary_key=primary_key,
                               validation_exceptions=validation_exceptions,
                               allow_to_many_replacement=atmr,
        					   page_size=page_size,
                               max_page_size=max_page_size,
                               serializer=serializer,
                               deserializer=deserializer,
                               includes=includes)

        if url_prefix is not None:
            prefix = url_prefix
        elif self.url_prefix is not None:
            prefix = self.url_prefix
        else:
            prefix = DEFAULT_URL_PREFIX
        blueprint = Blueprint(name, __name__, url_prefix=prefix)
        add_rule = blueprint.add_url_rule

        collection_url = '/{0}'.format(collection_name)
        resource_url = '{0}/<resource_id>'.format(collection_url)
        related_resource_url = '{0}/<relation_name>'.format(resource_url)
        to_many_resource_url = \
            '{0}/<related_resource_id>'.format(related_resource_url)
        relationship_url = \
            '{0}/relationships/<relation_name>'.format(resource_url)

        
        relationship_api_name = '{0}.relationships'.format(apiname)
        rapi_view = RelationshipAPI.as_view
        adftmr = allow_delete_from_to_many_relationships
        relationship_api_view = \
            rapi_view(relationship_api_name, session, model,
        
                      preprocessors=preprocessors_,
                      postprocessors=postprocessors_,
                      primary_key=primary_key,
                      validation_exceptions=validation_exceptions,
                      allow_to_many_replacement=allow_to_many_replacement,
        
                      allow_delete_from_to_many_relationships=adftmr)
        
        relationship_methods = READONLY_METHODS & methods
        if 'PATCH' in methods:
            relationship_methods |= WRITEONLY_METHODS
        add_rule(relationship_url, methods=relationship_methods,
                 view_func=relationship_api_view)

        collection_methods = frozenset(('POST', )) & methods
        add_rule(collection_url, view_func=api_view,
                 methods=collection_methods)
        collection_methods = frozenset(('GET', )) & methods
        collection_defaults = dict(resource_id=None, relation_name=None,
                                   related_resource_id=None)
        add_rule(collection_url, view_func=api_view,
                 methods=collection_methods, defaults=collection_defaults)

        resource_methods = frozenset(('DELETE', 'PATCH')) & methods
        add_rule(resource_url, view_func=api_view, methods=resource_methods)
        resource_methods = READONLY_METHODS & methods
        resource_defaults = dict(relation_name=None, related_resource_id=None)
        add_rule(resource_url, view_func=api_view, methods=resource_methods,
                 defaults=resource_defaults)

        related_resource_methods = READONLY_METHODS & methods
        related_resource_defaults = dict(related_resource_id=None)
        add_rule(related_resource_url, view_func=api_view,
                 methods=related_resource_methods,
                 defaults=related_resource_defaults)

        to_many_resource_methods = READONLY_METHODS & methods
        add_rule(to_many_resource_url, view_func=api_view,
                 methods=to_many_resource_methods)

        if allow_functions:
            eval_api_name = '{0}.eval'.format(apiname)
            eval_api_view = FunctionAPI.as_view(eval_api_name, session, model)
            eval_endpoint = '/eval{0}'.format(collection_url)
            eval_methods = ['GET']
            blueprint.add_url_rule(eval_endpoint, methods=eval_methods,
                                   view_func=eval_api_view)

        self.created_apis_for[model] = APIInfo(collection_name, blueprint.name,
                                               serializer, primary_key)
        return blueprint


	def model_for(self, collection_name):
        models = dict((info.collection_name, model)
                      for model, info in self.created_apis_for.items())
        try:
            return models[collection_name]
        except KeyError:
            raise ValueError('Collection name {0} unknown. Be sure to set the'
                             ' `collection_name` keyword argument when calling'
                             ' `create_api()`.'.format(collection_name))

    def url_for(self, model, **kw):

        collection_name = self.created_apis_for[model].collection_name
        blueprint_name = self.created_apis_for[model].blueprint_name
        api_name = APIManager.api_name(collection_name)
        parts = [blueprint_name, api_name]
        if 'relationship' in kw and kw.pop('relationship'):
            parts.append('relationships')
        url = flask_url_for('.'.join(parts), **kw)
        return url

    def collection_name(self, model):
        return self.created_apis_for[model].collection_name

    def serializer_for(self, model):
        return self.created_apis_for[model].serializer

    def primary_key_for(self, model):
        return self.created_apis_for[model].primary_key
        