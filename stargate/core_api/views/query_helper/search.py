import inspect
from sqlalchemy.orm.attributes import QueryableAttribute
from sqlalchemy.orm import ColumnProperty, joinedload
from .filter import Filter, create_filter
from ...proxy import primary_key_for
from .inclusion import Inclusions
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.orm.exc import NoResultFound

def is_like_list(instance, relation):
    if relation in instance._sa_class_manager:
        return instance._sa_class_manager[relation].property.uselist
    elif hasattr(instance, relation):
        attr = getattr(instance._sa_instance_state.class_, relation)
        if hasattr(attr, 'property'):
            return attr.property.uselist
    related_value = getattr(type(instance), relation, None)
    if isinstance(related_value, AssociationProxy):
        local_prop = related_value.local_attr.prop
        if isinstance(local_prop, RelProperty):
            return local_prop.uselist
    return False

def session_query(session, model):
	if hasattr(model, 'query'):
		if callable(model.query):
			query = model.query()
		else:
			query = model.query
		if hasattr(query, 'filter'):
			return query
	return session.query(model)

def primary_key_names(model):
    return [key for key, field in inspect.getmembers(model)
            if isinstance(field, QueryableAttribute)
            and isinstance(field.property, ColumnProperty)
            and field.property.columns[0].primary_key]

class Search():

	def __init__(self, session, model, relation = None, _initial_query=None):
		
		self.session = session
		self.model = model
		self.relation = relation
		self.initial_query = _initial_query

	def search_resource(self, pk_id = None, related_id = None, filters=None, sort=None, 
						group_by=None,page_size=None, page_number=None):
		
		if self.initial_query is not None:
			query = self._initial_query
		else:
			query = session_query(self.session, self.model)
		
		if pk_id is not None and self.relation is not None and related_id is not None:
			return self._search_one(query, pk_id, related_id)
		
		elif pk_id is not None and self.relation is not None:
			
			pk_name = primary_key_for(self.model)
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
			raise Exception("Unprocessiable entity")
	
	def _search_one(self, query, pk_value, related_id):
		
		try:
			pk_name = primary_key_for(self.model)
			query = session_query(self.session, self.model)
			query = query.filter(getattr(self.model, pk_name) == pk_value)
			resource = query.first()
			
			if self.relation is not None:
				resource = getattr(resource, self.relation)	
			return resource

		except NoResultFound as exception:
			detail = 'No result found'
			raise ResourceNotFound(self.model.__name__(), msg=detail)

		except MultipleResultsFound as exception:
			detail = 'Multiple results found'
			raise StargateException(msg=detail)

	def _search_collection(self, query,filters, sort, group_by, page_size, page_number):
		
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
					relation_model = get_related_model(model, field_name)
					field = getattr(relation_model, field_name_in_relation)
					query = query.join(relation_model)
					query = query.group_by(field)
				else:
					field = getattr(self.model, field_name)
					query = query.group_by(field)

		collection = query.paginate(page_number, page_size,error_out=False)
		return collection
