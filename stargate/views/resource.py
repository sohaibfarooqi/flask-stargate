from flask import request, json
from flask.views import MethodView
from ..proxy import manager_info, COLLECTION_NAME_FOR, SERIALIZER_FOR
from ..decorators import catch_processing_exceptions, catch_integrity_errors, requires_api_accept, requires_api_mimetype
from ..exception import StargateException
from ..query_helper.search import Search
from ..query_helper.inclusion import Inclusions
from .representation import InstanceRepresentation, CollectionRepresentation
from sqlalchemy import inspect
from flask_sqlalchemy import Pagination

FILTER_PARAM = 'filters'
SORT_PARAM = 'sort'
GROUP_PARAM = 'group'
FIELDS_PARAM = 'field'
EXPAND_PARAM = 'expand'
EXCLUDE_PARAM = 'exclude'
PAGE_SIZE_PARAM = 'page_size'
PAGE_NUMBER_PARAM = 'page_number'

STARGATE_DEFAULT_PAGE_NUMBER = 1
STARGATE_DEFAULT_PAGE_SIZE = 10
STARGATE_DEFAULT_MAX_PAGE_SIZE = 100

class ResourceAPI(MethodView):

	decorators = [  
                    requires_api_accept, 
                    requires_api_mimetype,
                    catch_processing_exceptions
                 ]

	def __init__(self, session, model, validation_exceptions = None, primary_key = None,*args,**kw):
        
		super(ResourceAPI, self).__init__()

		self.collection_name = manager_info(COLLECTION_NAME_FOR, model)
		
		self.session = session
		self.model = model

		self.validation_exceptions = tuple(validation_exceptions or ())

		self.primary_key = primary_key

	def get(self, pk_id = None, relation = None, related_id = None):
		
		query_string = request.args.to_dict()

		filters = query_string[FILTER_PARAM] if FILTER_PARAM in query_string else []
		sort = query_string[SORT_PARAM] if SORT_PARAM in query_string else []
		group_by = query_string[GROUP_PARAM] if GROUP_PARAM in query_string else []
		page_size = query_string[PAGE_SIZE_PARAM] if PAGE_SIZE_PARAM in query_string else STARGATE_DEFAULT_PAGE_SIZE
		page_number = query_string[PAGE_NUMBER_PARAM] if PAGE_NUMBER_PARAM in query_string else STARGATE_DEFAULT_PAGE_NUMBER
		fields = query_string[FIELDS_PARAM] if FIELDS_PARAM in query_string else []
		exclude = query_string[EXCLUDE_PARAM] if EXCLUDE_PARAM in query_string else []
		expand = query_string[EXPAND_PARAM] if EXPAND_PARAM in query_string else None
		
		if filters:
			filters = json.loads(filters)

		if sort:
			sort = [('-', value[1:]) if value.startswith('-') else ('+', value)
					for value in sort.split(',')]
		
		if group_by:
			group_by = group_by.split(',')
		
		if fields:
			fields = fields.split(',')
		
		if exclude:
			exclude = exclude.split(',')
		
		try:
			search_obj = Search(self.session, self.model, relation = relation)
		except Exception as exception:
			detail = 'Unable to construct query {0}'
			raise StargateException(msg=detail.format(exception))

		result_set = search_obj.search_resource(pk_id, related_id, filters = filters,sort = sort, 
												group_by = group_by, page_size = page_size, 
												page_number = page_number)
		if relation is None:
			serializer = manager_info(SERIALIZER_FOR, self.model)
		else:
			serializer	= manager_info(SERIALIZER_FOR, Inclusions.get_related_model(self.model, relation))
		
		if isinstance(result_set, Pagination):
			data = serializer(result_set.items, fields = fields, exclude = exclude, expand = expand)
			representation = CollectionRepresentation(self.model, page_size, page_number, result_set, data, 200)

		else:
			data = serializer(result_set, fields = fields, exclude = exclude, expand = expand)
			representation = InstanceRepresentation(self.model, pk_id, data,200)

		return representation.to_response()
