from .resource import ResourceAPI

class ApiViews():
	
	def add_resource_view(apiname, session, model, decorators_,
						primary_key_, page_size_,
						max_page_size_, serializer_,
						deserializer_, includes_):
		
		return ResourceAPI.as_view( apiname, session, model, decorators = decorators_,
									primary_key = primary_key_, page_size = page_size_,
									max_page_size = max_page_size_, serializer = serializer_,
									deserializer = deserializer_, includes = includes_)

	def add_function_view(*args, **kwargs):
		pass

	def add_schema_view(*args, **kwargs):
		pass

	