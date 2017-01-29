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
FIELDS = 'fields'
EXCLUDE = 'exclude'
PAGE_SIZE_PARAM = 'page_size'
PAGE_NUMBER_PARAM = 'page_number'

DEFAULT_PAGE_NUMBER = 1
DEFAULT_PAGE_SIZE = 10
DEFAULT_MAX_PAGE_SIZE = 100

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

		filters = query_string['filters'] if 'filter' in query_string else []
		sort = query_string['sort'] if 'sort' in query_string else []
		group_by = query_string['group'] if 'group' in query_string else []
		include = query_string['include'] if 'includes' in query_string else []
		fields = query_string['fields'] if 'fields' in query_string else []
		exclude = query_string['exclude'] if 'exclude' in query_string else []
		page_size = query_string['page_size'] if 'page_size' in query_string else DEFAULT_PAGE_SIZE
		page_number = query_string['page_number'] if 'page_number' in query_string else DEFAULT_PAGE_NUMBER
        
        
		if filters:
			filters = json.loads(query_string)

		if sort:
			sort = [('-', value[1:]) if value.startswith('-') else ('+', value)
					for value in sort.split(',')]

		if group_by:
			group_by = group_by.split(',')

		if include:
			pass

		if fields:
			pass

		if exclude:
			pass

		try:
			search_items = Search(self.session, self.model, 
									fields = fields, exclude = exclude)
		except Exception as exception:
			print(exception)
			detail = 'Unable to construct query'
			raise StargateException(msg=detail)

		result_set = search_items.search_resource(pk_id, filters = filters,sort = sort, 
													group_by = group_by, page_size=page_size, 
													page_number=page_number)
		
		if pk_id is not None:
			representation = InstanceRepresentation(self.model, pk_id, result_set,200)

		else:
			representation = CollectionRepresentation(self.model, self.page_size, result_set,200)

		return representation.to_response()
