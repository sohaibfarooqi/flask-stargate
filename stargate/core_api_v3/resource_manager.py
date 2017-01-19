from flask import Flask

class IllegalArgumentError(Exception):
    pass

class ResourceManager(object):
	"""Class to manage db Entities. 
	"""
	
	def __init__(self, app, sqlalchemy_session = None, flask_sqlalchemy_db = None,
                preprocessors = None, postprocessors = None, url_prefix = None):
        """Class Constructor"""

        if(isinstance(app, Flask))
            self.app = app
        else:
            msg = "Provided application instance should be `Flask` instance instead of %s" %str(type(app));
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

    def register_resource_as_api(self, *args, **kwargs):
        """Register callable endpoints for a particular resource.
        """ 
       
        
        if self._params_sanity_checks(args, kwargs):
            blueprint_name = str(uuid1())
            blueprint = self.create_resource_blueprint(blueprint_name, *args, **kw)
            self.blueprints.append(blueprint)

            if self.app is not None:
                self.app.register_blueprint(blueprint)

            else:
                msg = "Application not initilized"
                raise RuntimeError(msg)
        else:
            msg = "Failed params sanity check"
            raise RuntimeError(msg)

    def create_resource_blueprint( self, 
                                    name, 
                                    model, 
                                    methods = READONLY_METHODS,
                                    url_prefix = None, 
                                    collection_name = None,
                                    allow_functions = False, 
                                    only = None, 
                                    exclude = None,
                                    additional_attributes = None,
                                    validation_exceptions = None, 
                                    page_size = 10,
                                    max_page_size = 100, 
                                    preprocessors = None,
                                    postprocessors = None, 
                                    primary_key = None,
                                    serializer = None, 
                                    deserializer = None,
                                    includes = None, 
                                    to_many_replacement = False,
                                    delete_from_to_many_relationships = False,
                                    client_generated_ids = False):

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

        return True
    def register_resource_options(self, preprocessors, postprocessors, url_prefix):
        """Registering pre, post processsors and url_prefix"""

    def register_serialization_options(self, serializer, deserializer):

    def register_pagination_options(self, page_size, max_page_size):

    def register_resource_meta(self, name, model, methods, collection_name):

    def allow_function_on_resource(self, allow_functions):

    def resource_attrs_options(self, only, exclude, additional_attributes):
    
    def register_validation_errors(self, validation_exceptions = None):
    
    def register_included_model(self, includes):

    def resource_relationship_options(self, primary_key, allow_to_many_replacement, 
                                    allow_delete_from_to_many_relationships, allow_client_generated_ids):
    