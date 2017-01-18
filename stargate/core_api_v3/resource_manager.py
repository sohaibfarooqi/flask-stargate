class ResourceManager(object):
	"""Class to manage db Entities. 
	"""
	
	def __init__(self, app, session = None, flask_sqlalchemy_db = None,
                 preprocessors = None, postprocessors = None, url_prefix = None):
	"""Class Constructor"""

    def create_api_blueprint(self, name, model, methods = READONLY_METHODS,
                             url_prefix = None, collection_name = None,
                             allow_functions = False, only = None, exclude = None,
                             additional_attributes = None,
                             validation_exceptions = None, page_size = 10,
                             max_page_size = 100, preprocessors = None,
                             postprocessors = None, primary_key = None,
                             serializer = None, deserializer = None,
                             includes = None, allow_to_many_replacement = False,
                             allow_delete_from_to_many_relationships = False,
                             allow_client_generated_ids = False):