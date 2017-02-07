from flask import request
from flask.views import MethodView
from ..proxy import url_for, serializer_for, collection_name_for
from ..decorators import catch_processing_exceptions, catch_integrity_errors, requires_api_accept, requires_api_mimetype
from ..exception import StargateException
from .query_helper.search import Search
from .representation import InstanceRepresentation, CollectionRepresentation
from sqlalchemy import inspect

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

	def __init__(self, session, model, primary_key = None,validation_exceptions = None, 
				includes = None,fields = None,exclude = None,*args,**kw):
        
		super(ResourceAPI, self).__init__()

		self.collection_name = collection_name_for(model)
		
		self.session = session
		self.model = model

		self.fields = fields
		self .exclude = exclude

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
			filters = json.loads(query_string)

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
			search_obj = Search(self.session, self.model)
		except Exception as exception:
			detail = 'Unable to construct query {0}'
			raise StargateException(msg=detail.format(exception))

		result_set = search_obj.search_resource(pk_id, relation, related_id, filters = filters,sort = sort, 
												group_by = group_by, page_size = page_size, 
												page_number = page_number)
		serializer = serializer_for(self.model)
			
		if pk_id is not None:
			data = serializer(result_set, fields = fields, exclude = exclude, expand = expand)
			representation = InstanceRepresentation(self.model, pk_id, result_set,200)

		else:
			data = serializer(result_set.items, fields = fields, exclude = exclude, expand = expand)
			representation = CollectionRepresentation(self.model, page_size, page_number, result_set, data, 200)

		return representation.to_response()
