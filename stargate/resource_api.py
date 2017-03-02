from flask import request, json, jsonify
from flask.views import MethodView
from .proxy import manager_info, COLLECTION_NAME_FOR, SERIALIZER_FOR, PRIMARY_KEY_FOR, DESERIALIZER_FOR
from .decorators import catch_processing_exceptions, catch_integrity_errors, requires_api_accept, requires_api_mimetype
from .exception import StargateException, ResourceNotFound
from .query_helper.search import Search, session_query
from .query_helper.inclusion import Inclusions
from .representation import InstanceRepresentation, CollectionRepresentation
from flask_sqlalchemy import Pagination
from .utils import get_resource, is_like_list, has_field, string_to_datetime

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
        
		super(ResourceAPI, self).__init__(*args,**kw)

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
		fields = query_string[FIELDS_PARAM] if FIELDS_PARAM in query_string else []
		exclude = query_string[EXCLUDE_PARAM] if EXCLUDE_PARAM in query_string else []
		expand = query_string[EXPAND_PARAM] if EXPAND_PARAM in query_string else None
		page_number = int(query_string[PAGE_NUMBER_PARAM]) if PAGE_NUMBER_PARAM in query_string else STARGATE_DEFAULT_PAGE_NUMBER
		page_size = int(query_string[PAGE_SIZE_PARAM]) if PAGE_SIZE_PARAM in query_string else STARGATE_DEFAULT_PAGE_SIZE
		page_size = page_size if page_size <= STARGATE_DEFAULT_MAX_PAGE_SIZE else STARGATE_DEFAULT_MAX_PAGE_SIZE

		if filters:
			filters = json.loads(filters)

		if sort:
			sort = [('-', value[1:]) if value.startswith('-') else ('+', value)
					for value in sort.split(',')]
		
		if group_by:
			group_by = group_by.split(',')
			group_by.append(manager_info(PRIMARY_KEY_FOR, self.model))
		
		if fields:
			fields = fields.split(',')
		
		if exclude:
			exclude = exclude.split(',')
		
		try:
			search_obj = Search(self.session, self.model, relation = relation)
		except Exception as exception:
			detail = 'Unable to construct query {0}'
			raise StargateException(msg=detail.format(exception))

		result_set = search_obj.search_resource(pk_id, related_id, filters = filters, sort = sort, 
												group_by = group_by, page_size = page_size, 
												page_number = page_number)
		if relation is None:
			serializer = manager_info(SERIALIZER_FOR, self.model)
		else:
			serializer	= manager_info(SERIALIZER_FOR, Inclusions.get_related_model(self.model, relation))
		
		if isinstance(result_set, Pagination):
			data = serializer(result_set.items, fields = fields, exclude = exclude, expand = expand)
			representation = CollectionRepresentation(self.model, data, 200)
			return representation.to_response(page_size = page_size, page_number = page_number, pagination = result_set)
		else:
			data = serializer(result_set, fields = fields, exclude = exclude, expand = expand)
			representation = InstanceRepresentation(self.model, pk_id, data, 200)
			return representation.to_response()

		

	def post(self):

		try:
			data = json.loads(request.get_data()) or {}
		
		except Exception as exception:
			raise StargateException("Unable to decode Request Body : ".format(str(exception)))

		try:
			deserializer = manager_info(DESERIALIZER_FOR, self.model)
			instance = deserializer(data)
			
			if isinstance(instance, list):
				self.session.add_all(instance)
			else:
				self.session.add(instance)
		
			self.session.flush()
			self.session.commit()
		
		except Exception as ex:
			self.session.rollback()
			self.session.close()
			raise StargateException("Unable to save object Error: `{0}`".format(str(ex)))

		relations = Inclusions.get_relations(self.model)
		relations = ",".join(relations)
		serializer = manager_info(SERIALIZER_FOR, self.model)
		result = serializer(instance, expand = relations)
		
		if isinstance(instance, list):
			representation = CollectionRepresentation(self.model, result, 201)
		
		else:
			pk_name = manager_info(PRIMARY_KEY_FOR, self.model)
			pk_val = getattr(instance, pk_name)
			representation = InstanceRepresentation(self.model, pk_val, result, 201)

		return representation.to_response()

	def patch(self, pk_id):
		
		try:
			data = json.loads(request.get_data()) or {}
		
		except Exception as exception:
			raise StargateException("Unable to decode Request Body : ".format(str(exception)))
		
		primary_resource = get_resource(self.session, self.model, pk_id)
		data = data.pop('data', {})
		
		links = data.pop('_embedded', {})
		
		for linkname, link in links.items():

			linkage = link['data']
			related_model = Inclusions.get_related_model(self.model, linkname)
            
			if is_like_list(primary_resource, linkname):

				newvalue = []
				not_found = []

				for rel in linkage:

					id_ = rel['id']
					inst = get_resource(self.session, related_model, id_)

					if inst is None:
						not_found.append((id_, type_))
					else:
						newvalue.append(inst)
			else:
				
				if linkage is None:
					newvalue = None
				else:
					id_ = linkage['id']
					inst = get_resource(self.session, related_model, id_)
					newvalue = inst
					setattr(primary_resource, linkname, newvalue)

			data = data.pop('attributes', {})

			for field in data:
				if not has_field(self.model, field):
					detail = "Model does not have field '{0}'".format(field)
					raise StargateException(detail=detail)

			data = dict((k, string_to_datetime(self.model, k, v)) for k, v in data.items())

			if data:
				for field, value in data.items():
					setattr(primary_resource, field, value)
			self.session.add(primary_resource)
			self.session.commit()
			serializer = manager_info(SERIALIZER_FOR, self.model)
			result = serializer(primary_resource)
			repr = InstanceRepresentation(self.model, pk_id, result, 200)
			return repr.to_response()

	def delete(self, pk_id):
	
		try:
			pk_name = manager_info(PRIMARY_KEY_FOR, self.model)
			query = session_query(self.session, self.model)
			query = query.filter(getattr(self.model, pk_name) == pk_id)
			resource = query.one()
			print(resource)
			self.session.delete(resource)
			self.session.commit()

		except NoResultFound as exception:
			detail = 'No result found'
			raise ResourceNotFound(self.model.__name__, msg=detail)

		except MultipleResultsFound as exception:
			detail = 'Multiple results found'
			raise StargateException(msg=detail)

		return jsonify({'status_code': 204, 'message': 'No Content'})