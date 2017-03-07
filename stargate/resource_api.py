"""Main API view for all resources. Provide GET, POST, PATCH, DELETE HTTP method support.
Endpoint for methods may vary in case of collection and instance. Support all db transction 
which can result in case of mentioned HTTP methods. More options can be found in docs of individual func.

"""
from flask import request, json, jsonify
from flask.views import MethodView
from .resource_info import resource_info
from .decorators import catch_processing_exceptions, catch_integrity_errors, requires_api_accept, requires_api_mimetype
from .exception import ValidationError, DatabaseError, MissingData, MissingPrimaryKey, UnknownField, UnknownRelation
from .search import Search, session_query
from .utils import get_related_model, get_relations
from .representation import InstanceRepresentation, CollectionRepresentation
from flask_sqlalchemy import Pagination
from .utils import get_resource, is_like_list, has_field, string_to_datetime
from .const import PaginationConst, QueryStringConst, ResourceInfoConst, SerializationConst

class ResourceAPI(MethodView):
	"""This class is used to provide view functions against resources. By default on ``GET`` method
	is exposed. It accept options like database session, model class, primary key and any other 
	parameter that parent class :class:`~flask.views.MethodView` provides.

	It applies :meth:`~stargate.decorators.requires_api_accept`, :meth:`~stargate.decorators.requires_api_mimetype`
	:meth:`~stargate.decorators.catch_processing_exceptions` decorators by default.

	Example usage for this class: 

	.. sourcecode:: python
		
		from resource_api import ResourceAPI

		ResourceAPI.as_view(session, model)

		#Specify primary_key id
		ResourceAPI.as_view(session, model, primary_key = 'ser_id')

		#MethodView args example
		ResourceAPI.as_view(session, model, primary_key = 'ser_id', _external=True)

	"""
	decorators = [  
                    requires_api_accept, 
                    requires_api_mimetype,
                    catch_processing_exceptions
                 ]

	def __init__(self, session, model, primary_key = None,*args,**kw):
        
		super(ResourceAPI, self).__init__(*args,**kw)

		# self.collection_name = resource_info(ResourceInfoConst.COLLECTION_NAME, model)
		
		self.session = session
		self.model = model

		self.primary_key = primary_key
				

	def get(self, pk_id = None, relation = None, related_id = None):
		"""Provides HTTP GET Method against a resource. Can be a collection or single instance.
		For more information about method and options check `get method`
		
		
		:param pk_id: resource primary key id.
		:param relation: related collection name. 
		:param related_id: primary key id od related resource 
		:return: :class:`~stargate.representation.Representation`

		For request query string options check `docs get.collection`
		
		"""
		try:
			query_string = request.args.to_dict()
			"""Get Search critertia from query string. Assign default ``[]`` to filters, fields, exclude
			sort and groupby. Assign default pagination params according to `stargate.const.PaginationConst` 
			page_number, page_size.
			"""
			filters = query_string[QueryStringConst.FILTER] if QueryStringConst.FILTER in query_string else []
			sort = query_string[QueryStringConst.SORT] if QueryStringConst.SORT in query_string else []
			group_by = query_string[QueryStringConst.GROUP] if QueryStringConst.GROUP in query_string else []
			fields = query_string[QueryStringConst.FIELDS] if QueryStringConst.FIELDS in query_string else []
			exclude = query_string[QueryStringConst.EXCLUDE] if QueryStringConst.EXCLUDE in query_string else []
			expand = query_string[QueryStringConst.EXPAND] if QueryStringConst.EXPAND in query_string else None
			page_number = int(query_string[QueryStringConst.PAGE_NUMBER]) if QueryStringConst.PAGE_NUMBER in query_string else PaginationConst.PAGE_NUMBER
			page_size = int(query_string[QueryStringConst.PAGE_SIZE]) if QueryStringConst.PAGE_SIZE in query_string else PaginationConst.PAGE_SIZE
			page_size = page_size if page_size <= PaginationConst.MAX_PAGE_SIZE else PaginationConst.MAX_PAGE_SIZE
		
		except Exception  as e:
			raise ValidationError(msg=str(e))

		"""Parse params received in request query string
		"""
		if filters:
			try:
				filters = filters.strip().rstrip(',').lstrip(',')
				filters = json.loads(filters.strip())
			except Exception as e:
				raise ValidationError(msg=str(e))

		if sort:
			sort = sort.strip().rstrip(',').lstrip(',')
			sort = [('-', value[1:]) if value.startswith('-') else ('+', value)
					for value in sort.split(',')]
		
		if group_by:
			group_by = group_by.strip().rstrip(',').lstrip(',')
			group_by = group_by.split(',')
			group_by.append(resource_info(ResourceInfoConst.PRIMARY_KEY, self.model))
		
		if fields:
			fields = fields.strip().rstrip(',').lstrip(',')
			fields = fields.split(',')
		
		if exclude:
			exclude = exclude.strip().rstrip(',').lstrip(',')
			exclude = exclude.split(',')
		
		try:
			#initilize search query
			search_obj = Search(self.session, self.model, relation = relation)
		except Exception as exception:
			detail = 'Unable to construct query {0}'
			raise DatabaseError(msg=detail.format(exception))

		#Search collection/resource using meth: `stargate.search.Search.search_resource`.
		result_set = search_obj.search_resource(pk_id, related_id, filters = filters, sort = sort, 
												group_by = group_by, page_size = page_size, 
												page_number = page_number)
		
		#If related collection/resource get serializer for related model else primary model.
		if relation is None:
			serializer = resource_info(ResourceInfoConst.SERIALIZER, self.model)
		else:
			serializer	= resource_info(ResourceInfoConst.SERIALIZER, get_related_model(self.model, relation))
		
		"""If result set is `flask_sqlalchemy.Pagination` object, make response of type
		`stargate.representation.CollectionRepresentation` otherwise 
		`stargate.representation.InstanceRepresentation`
		"""
		if isinstance(result_set, Pagination):
			data = serializer(result_set.items, fields = fields, exclude = exclude, expand = expand)
			representation = CollectionRepresentation(self.model, data, 200)
			return representation.to_response(page_size = page_size, page_number = page_number, pagination = result_set)
		else:
			data = serializer(result_set, fields = fields, exclude = exclude, expand = expand)
			representation = InstanceRepresentation(self.model, pk_id, data, 200)
			return representation.to_response()

		

	def post(self):
		"""Create resource(s) against data provided in payload. 
		
		:return: :class:`~stargate.representation.Representation` instance.

		Raise Following exceptions:
		 - :class:`~stargate.exception.InvalidPayload` if fails to convert payload to JSON. 
		 - :class:`stargate.exception.DatabaseError` If ``session.commit()`` fails. 
		
		For more information on POST method and payload options check `post method docs`

		"""
		try:
			#Load JSON from payload
			data = json.loads(request.get_data()) or {}
		
		except Exception as exception:
			raise ValidationError("Unable to decode Request Body : ".format(str(exception)))

		try:
			#Deserialize data
			deserializer = resource_info(ResourceInfoConst.DESERIALIZER, self.model)
			instance = deserializer(data)
			
			#Add object to db session
			if isinstance(instance, list):
				self.session.add_all(instance)
			else:
				self.session.add(instance)
		
			self.session.flush()
			self.session.commit()
		
		except Exception as ex:
			self.session.rollback()
			self.session.close()
			raise DatabaseError("Unable to save object Error: `{0}`".format(str(ex)))

		#FIXME: How to return response as representation?
		#Get all relations for serialization
		relations = get_relations(self.model)
		relations = ",".join(relations)
		serializer = resource_info(ResourceInfoConst.SERIALIZER, self.model)
		#Serialize data with all resource expanded
		result = serializer(instance, expand = relations)
		
		if isinstance(instance, list):
			representation = CollectionRepresentation(self.model, result, 201)
		
		else:
			pk_name = resource_info(ResourceInfoConst.PRIMARY_KEY, self.model)
			pk_val = getattr(instance, pk_name)
			representation = InstanceRepresentation(self.model, pk_val, result, 201)

		return representation.to_response()

	def patch(self, pk_id):
		"""Update resource(s) against data provided in payload. Can create new resources on fly as well
		
		:param pk_id: primary key id of resource to be updated.
		:return: :class:`~stargate.representation.Representation` instance.

		Raise following exceptions:
		
		 - :class:`~stargate.exception.InvalidPayload` if fails to convert payload to JSON. 
		 - :class:`stargate.exception.DatabaseError` If ``session.commit()`` fails. 
		 - :class:`~stargate.exception.MissingData` if data key is missing either in primary attribute
			of ``_embedded`` resource. 
		 - :class:`~stargate.exception.MissingPrimaryKey` if primary key id is missing.
		 - :class:`~stargate.exception.UnknownField` if field doesnot exists on resource.

		For more information on PATCH method and payload options check `post method docs`

		"""
		try:
			data = json.loads(request.get_data()) or {}
		
		except Exception as exception:
			raise ValidationError("Unable to decode Request Body : ".format(str(exception)))
		
		primary_resource = get_resource(self.session, self.model, pk_id)
		#get data out of payload
		data = data.pop(SerializationConst.DATA, {})
		#Get embedded resource
		links = data.pop(SerializationConst.EMBEDDED, {})
		#Get all relations of primary resource
		all_links = get_relations(self.model)
		
		for linkname, link in links.items():
			
			if SerializationConst.DATA not in link:
				raise MissingData(link)

			if linkname not in all_links:
				raise UnknownRelation(linkname, self.model)

			#Get the data out of related resource
			linkage = link[SerializationConst.DATA]
			related_model = get_related_model(self.model, linkname)
            
            #If TO_MANY append all
			if is_like_list(primary_resource, linkname):

				newvalue = []
				fk_name = resource_info(ResourceInfoConst.PRIMARY_KEY, related_model)
				for rel in linkage:
					
					if fk_name in rel:
						inst = get_resource(self.session, related_model, rel[fk_name])
						newvalue.append(inst)
					else:
						raise MissingPrimaryKey(rel)
			
			#If TO_ONE
			else:
				
				if linkage is None:
					newvalue = None
				else:
					fk_name = resource_info(ResourceInfoConst.PRIMARY_KEY, related_model)
					
					if fk_name in linkage:
						inst = get_resource(self.session, related_model, linkage[fk_name])
						newvalue = inst
						setattr(primary_resource, linkname, newvalue)
					else:
						raise MissingPrimaryKey(msg="Missing primary key in request")

			#Pop primary resource attributes
			data = data.pop(SerializationConst.ATTRIBUTES, {})

			for field in data:
				if not has_field(self.model, field):
					detail = "Model does not have field '{0}'".format(field)
					raise UnknownField(detail=detail)

			#Parse any datetime field(s)
			data = dict((k, string_to_datetime(self.model, k, v)) for k, v in data.items())

			if data:
				for field, value in data.items():
					setattr(primary_resource, field, value)
			
			try:
				self.session.add(primary_resource)
				self.session.commit()
			except Exception as e:
				raise DatabaseError("Unable to update resource: {0}".format(str(e)))
			
			#FIXME: How to return proper representation using API response style?
			serializer = resource_info(ResourceInfoConst.SERIALIZER, self.model)
			result = serializer(primary_resource)
			
			repr = InstanceRepresentation(self.model, pk_id, result, 200)
			return repr.to_response()

	def delete(self, pk_id):
		"""Delete resource against id provided in path param.

		:param pk_id: primary key id of resource to be updated.
		:return: :class:`~stargate.representation.Representation` instance.
		
		Raise following exception if operation fail:
		 
		 - :class:`stargate.exception.DatabaseError` If ``session.commit()`` fails. 
		 
		For more information on DELETE method and payload options check `post method docs`

		"""
		try:
			resource = get_resource(self.session, self.model, pk_id)
			self.session.delete(resource)
			self.session.commit()
		except Exception as e:
			raise DatabaseError("Unable to Delete resource: {0}".format(str(e)))

		return jsonify({'status_code': 204, 'message': 'No Content'})