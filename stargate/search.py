"""Search utility for API. Can search collection, single instance, related collection, related resource.
Provides filteration, grouping, ordering on collections and related collections.

"""

import inspect
from sqlalchemy.orm.attributes import QueryableAttribute
from sqlalchemy.orm import ColumnProperty, joinedload
from .filter import Filter, create_filter
from .resource_info import resource_info
from .utils import get_related_model, is_like_list, session_query, get_resource
from .const import ResourceInfoConst


def primary_key_names(model):
    return [key for key, field in inspect.getmembers(model)
            if isinstance(field, QueryableAttribute)
            and isinstance(field.property, ColumnProperty)
            and field.property.columns[0].primary_key]

class Search():
	"""Search class for searching collection or instance. Search through collection
	based on filters, ordering, grouping and pagination. Search single resource provided
	primary key id. This class can also search related collection or instance.

	:param session: SQLAlchemy session object.
	:param model: user defined model class Using :class:`~flask_sqlalchemy.SQLALchemy.Model`. 
	:param relation: If related collection/instance need to be searched. 
	:param initial_query: initial query to be appended to search query in this class
		
	"""
	def __init__(self, session, model, relation = None, _initial_query=None):
		
		self.session = session
		self.model = model
		self.relation = relation
		self.initial_query = _initial_query

	def search_resource(self, pk_id = None, related_id = None, filters=None, sort=None, 
						group_by=None,page_size=None, page_number=None):
		"""Public method `Search` class. This method can be used to perform search
		on either related collection or primary collection. Moreover it can also be used to 
		search single instances.

		:param pk_id: Primary key id for resource to be fetched.
		:param related_id: Primary key id for related resource to be fetched. 
		:param filters: filters str representation received in request query string. 
		:param sort: sort attribute(s) for collection.
		:param group_by: group attribute(s) for collection.
		:param page_size: page_size for collection.
		:param page_number: page_number for collection.

		"""
		if self.initial_query is not None:
			query = self._initial_query
		else:
			query = session_query(self.session, self.model)
		
		if pk_id is not None and self.relation is not None and related_id is not None:
			return self._search_one(query, pk_id, related_id)
		
		elif pk_id is not None and self.relation is not None:
			
			pk_name = resource_info(ResourceInfoConst.PRIMARY_KEY, self.model)
			primary_resource = query.filter(getattr(self.model, pk_name) == pk_id).first()
			related_model = getattr(primary_resource, self.relation)

			if is_like_list(primary_resource, self.relation):
				query = session_query(self.session, related_model[0].__class__)
				return self._search_collection(query, filters, sort, group_by, page_size, page_number)
		
			else:
				return related_model
		
		elif pk_id is not None:
			return self._search_one(query, pk_id, None)
		
		else:
			return self._search_collection(query, filters, sort, group_by, page_size, page_number)
	
	def _search_one(self, query, pk_value, related_id):
		"""This method is internally used by search_resource if a single resource need to be fetched.
		This method is invoked in `id` for primary resource is not None or related resource `id` is set.

		:param query: Initial query from :meth:`~stargate.search.Search.search_resource()`
		:param pk_value: Primary key value for resource to be fetched. 
		:param related_id: Primary key id for related resource to be fetched. 
		
		"""
		resource = get_resource(self.session, self.model, pk_value)
		if self.relation is not None:
			resource = getattr(resource, self.relation)	
		return resource

	def _search_collection(self, query,filters, sort, group_by, page_size, page_number):
		"""This method is internally used by search_resource if a collection resource need 
		to be fetched.
		
		:param query: Initial query from :meth:`~stargate.search.Search.search_resource()`
		:param filters: filters str representation received in request query string. 
		:param sort: sort attribute(s) for collection.
		:param group_by: group attribute(s) for collection.
		:param page_size: page_size for collection.
		:param page_number: page_number for collection.
		
		"""
		if filters:
			filters = [Filter.from_dictionary(self.model, f) for f in filters]
			filters = [create_filter(self.model, f) for f in filters]
			query = query.filter(*filters)
	    
		if sort:
			for (symbol, field_name) in sort:
				direction_name = 'asc' if symbol == '+' else 'desc'
				if '.' in field_name:
					field_name, field_name_in_relation = field_name.split('.')
					relation_model = aliased(get_related_model(self.model, field_name))
					field = getattr(relation_model, field_name_in_relation)
					direction = getattr(field, direction_name)
					query = query.join(relation_model)
					query = query.order_by(direction())
				else:
					field = getattr(self.model, field_name)
					direction = getattr(field, direction_name)
					query = query.order_by(direction())
		if group_by:
			for field_name in group_by:
				if '.' in field_name:
					field_name, field_name_in_relation = field_name.split('.')
					relation_model = get_related_model(self.model, field_name)
					field = getattr(relation_model, field_name_in_relation)
					query = query.join(relation_model)
					query = query.group_by(field)
				else:
					field = getattr(self.model, field_name)
					query = query.group_by(field)

		collection = query.paginate(page_number, page_size,error_out=False)
		return collection
