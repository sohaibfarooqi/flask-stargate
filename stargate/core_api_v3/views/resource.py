from flask import request
from flask.views import MethodView
from ..proxy import url_for, serializer_for, collection_name_for
from ..mimerender import requires_json_api_accept, requires_json_api_mimetype
from ..errors import catch_processing_exceptions, catch_integrity_errors
from ..exception import StargateException
from .query_helper.search import Search
from .representation import InstanceRepresentation, CollectionRepresentation

FILTER_PARAM = 'filters'
SORT_PARAM = 'sort'
GROUP_PARAM = 'group'
INCLUDE_ATTRS_PARAM = 'include_f'
EXCLUDE_ATTRS_PARAM = 'exclude_f'
INCLUDE_RESOURCE_PARAM = 'include_r'
EXCLUDE_RESOURCE_PARAM = 'exclude_r'
PAGE_SIZE_PARAM = 'page_size'
PAGE_NUMBER_PARAM = 'page_number'

STARGATE_DEFAULT_PAGE_NUMBER = 1
STARGATE_DEFAULT_PAGE_SIZE = 10
STARGATE_DEFAULT_MAX_PAGE_SIZE = 100

class ResourceAPI(MethodView):

	decorators = [  
                    requires_json_api_accept, 
                    requires_json_api_mimetype,
                    catch_processing_exceptions
                 ]

	def __init__(self, session, model, primary_key=None, serializer=None, deserializer=None,
                 validation_exceptions=None, includes=None,fields=None,exclude=None,
                 page_size=None, per_page=None, *args,**kw):
        
		super(ResourceAPI, self).__init__()

		self.collection_name = collection_name_for(model)

		self.default_includes = includes


		self.session = session
		self.model = model

		self.fields = fields
		self .exclude = exclude

		self.page_size = page_size
		self.per_page = per_page

		self.serialize = serializer
		self.deserialize = deserializer

		self.validation_exceptions = tuple(validation_exceptions or ())

		self.primary_key = primary_key

	def get(self, pk_id = None):
		
		query_string = request.args.to_dict()

		filters = query_string[FILTER_PARAM] if FILTER_PARAM in query_string else []
		sort = query_string[SORT_PARAM] if SORT_PARAM in query_string else []
		group_by = query_string[GROUP_PARAM] if GROUP_PARAM in query_string else []
		include_resource = query_string[INCLUDE_RESOURCE_PARAM] if INCLUDE_RESOURCE_PARAM in query_string else []
		exclude_resource = query_string[EXCLUDE_RESOURCE_PARAM] if EXCLUDE_RESOURCE_PARAM in query_string else []
		include_fields = query_string[INCLUDE_ATTRS_PARAM] if INCLUDE_ATTRS_PARAM in query_string else []
		exclude_fields = query_string[EXCLUDE_ATTRS_PARAM] if EXCLUDE_ATTRS_PARAM in query_string else []
		page_size = query_string[PAGE_SIZE_PARAM] if PAGE_SIZE_PARAM in query_string else STARGATE_DEFAULT_PAGE_SIZE
		page_number = query_string[PAGE_NUMBER_PARAM] if PAGE_NUMBER_PARAM in query_string else STARGATE_DEFAULT_PAGE_NUMBER

        
		if filters:
			filters = json.loads(query_string)

		if sort:
			sort = [('-', value[1:]) if value.startswith('-') else ('+', value)
					for value in sort.split(',')]
		
		if group_by:
			group_by = group_by.split(',')

		if include_resource:
			include_resource = include_resource.split(',')

		if exclude_resource:
			exclude_resource = exclude_resource.split(',')

		if include_fields:
			include_fields = include_fields.split(',')

		if exclude_fields:
			exclude_fields = exclude_fields.split(',')
		

		try:
			search_items = Search(self.session, self.model)
		except Exception as exception:
			detail = 'Unable to construct query'
			raise StargateException(msg=detail)

		result_set = search_items.search_resource(pk_id, filters = filters,sort = sort, 
													group_by = group_by, page_size=page_size, 
													page_number=page_number)
		serializer = serializer_for(self.model)
			
		if pk_id is not None:
			data = serializer(result_set, include_resource=include_resource, exclude_resource=exclude_resource)
			representation = InstanceRepresentation(self.model, pk_id, result_set,200)

		else:
			data = serializer(result_set.items, include_resource=include_resource, exclude_resource=exclude_resource)
			representation = CollectionRepresentation(self.model, self.page_size, result_set, data, 200)

		return representation.to_response()
