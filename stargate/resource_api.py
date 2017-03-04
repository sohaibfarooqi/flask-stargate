"""Main API view for all resources. Provide GET, POST, PATCH, DELETE HTTP method support.
Endpoint for methods may vary in case of collection and instance. Support all db transction 
which can result in case of mentioned HTTP methods. More options can be found in docs of individual func.

"""
from flask import request, json, jsonify
from flask.views import MethodView
from .proxy import manager_info
from .decorators import catch_processing_exceptions, catch_integrity_errors, requires_api_accept, requires_api_mimetype
from .exception import StargateException, ResourceNotFound
from .search import Search, session_query
from .utils import get_related_model, get_relations
from .representation import InstanceRepresentation, CollectionRepresentation
from flask_sqlalchemy import Pagination
from .utils import get_resource, is_like_list, has_field, string_to_datetime
from .const import PaginationConst, QueryStringConst, ResourceInfoConst, SerializationConst

class ResourceAPI(MethodView):

	decorators = [  
                    requires_api_accept, 
                    requires_api_mimetype,
                    catch_processing_exceptions
                 ]

	def __init__(self, session, model, primary_key = None,*args,**kw):
        
		super(ResourceAPI, self).__init__(*args,**kw)

		self.collection_name = manager_info(ResourceInfoConst.COLLECTION_NAME_FOR, model)
		
		self.session = session
		self.model = model

		self.primary_key = primary_key
				

	def get(self, pk_id = None, relation = None, related_id = None):
		
		query_string = request.args.to_dict()

		filters = query_string[QueryStringConst.FILTER] if QueryStringConst.FILTER in query_string else []
		sort = query_string[QueryStringConst.SORT] if QueryStringConst.SORT in query_string else []
		group_by = query_string[QueryStringConst.GROUP] if QueryStringConst.GROUP in query_string else []
		fields = query_string[QueryStringConst.FIELDS] if QueryStringConst.FIELDS in query_string else []
		exclude = query_string[QueryStringConst.EXCLUDE] if QueryStringConst.EXCLUDE in query_string else []
		expand = query_string[QueryStringConst.EXPAND] if QueryStringConst.EXPAND in query_string else None
		page_number = int(query_string[QueryStringConst.PAGE_NUMBER]) if QueryStringConst.PAGE_NUMBER in query_string else PaginationConst.PAGE_NUMBER
		page_size = int(query_string[QueryStringConst.PAGE_SIZE]) if QueryStringConst.PAGE_SIZE in query_string else PaginationConst.PAGE_SIZE
		page_size = page_size if page_size <= PaginationConst.MAX_PAGE_SIZE else PaginationConst.MAX_PAGE_SIZE

		if filters:
			filters = json.loads(filters)

		if sort:
			sort = [('-', value[1:]) if value.startswith('-') else ('+', value)
					for value in sort.split(',')]
		
		if group_by:
			group_by = group_by.split(',')
			group_by.append(manager_info(ResourceInfoConst.PRIMARY_KEY_FOR, self.model))
		
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
			serializer = manager_info(ResourceInfoConst.SERIALIZER_FOR, self.model)
		else:
			serializer	= manager_info(ResourceInfoConst.SERIALIZER_FOR, get_related_model(self.model, relation))
		
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
			deserializer = manager_info(ResourceInfoConst.DESERIALIZER_FOR, self.model)
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

		relations = get_relations(self.model)
		relations = ",".join(relations)
		serializer = manager_info(ResourceInfoConst.SERIALIZER_FOR, self.model)
		result = serializer(instance, expand = relations)
		
		if isinstance(instance, list):
			representation = CollectionRepresentation(self.model, result, 201)
		
		else:
			pk_name = manager_info(ResourceInfoConst.PRIMARY_KEY_FOR, self.model)
			pk_val = getattr(instance, pk_name)
			representation = InstanceRepresentation(self.model, pk_val, result, 201)

		return representation.to_response()

	def patch(self, pk_id):
		
		try:
			data = json.loads(request.get_data()) or {}
		
		except Exception as exception:
			raise StargateException("Unable to decode Request Body : ".format(str(exception)))
		
		primary_resource = get_resource(self.session, self.model, pk_id)
		data = data.pop(SerializationConst.DATA, {})
		
		links = data.pop(SerializationConst._EMBEDDED, {})
		
		for linkname, link in links.items():

			linkage = link[SerializationConst.DATA]
			related_model = get_related_model(self.model, linkname)
            
			if is_like_list(primary_resource, linkname):

				newvalue = []
				fk_name = manager_info(ResourceInfoConst.PRIMARY_KEY_FOR, related_model)
				for rel in linkage:
					
					if fk_name in rel:
						inst = get_resource(self.session, related_model, rel[fk_name])
						newvalue.append(inst)
			else:
				
				if linkage is None:
					newvalue = None
				else:
					fk_name = manager_info(ResourceInfoConst.PRIMARY_KEY_FOR, related_model)
					if fk_name in linkage:
						inst = get_resource(self.session, related_model, linkage[fk_name])
						newvalue = inst
						setattr(primary_resource, linkname, newvalue)

			data = data.pop(SerializationConst.ATTRIBUTES, {})

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
			
			serializer = manager_info(ResourceInfoConst.SERIALIZER_FOR, self.model)
			result = serializer(primary_resource)
			
			repr = InstanceRepresentation(self.model, pk_id, result, 200)
			return repr.to_response()

	def delete(self, pk_id):

		resource = get_resource(self.session, self.model, pk_id)
		self.session.delete(resource)
		self.session.commit()

		return jsonify({'status_code': 204, 'message': 'No Content'})