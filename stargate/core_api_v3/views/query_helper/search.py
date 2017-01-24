import inspect
from sqlalchemy.orm.attributes import QueryableAttribute
from sqlalchemy.orm import ColumnProperty
from .filter import Filter

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

	def __init__(self, session, model, filters=None, sort=None, group_by=None,
           _initial_query=None):
		
		self.session = session
		self.model = model
		self.filters = filters
		self.sort = sort
		self.group_by = group_by
		self.initial_query = _initial_query
	
	def search_collection(self):
	    if self.initial_query is not None:
	        query = _initial_query
	    else:
	        query = session_query(self.session, self.model)

	    filters = [Filter.from_dictionary(model, f) for f in self.filters]
	    filters = [create_filter(model, f) for f in filters]
	    query = query.filter(*filters)

	    if self.sort:
	        for (symbol, field_name) in self.sort:
	            direction_name = 'asc' if symbol == '+' else 'desc'
	            if '.' in field_name:
	                field_name, field_name_in_relation = field_name.split('.')
	                relation_model = aliased(get_related_model(self.model, self.field_name))
	                field = getattr(relation_model, field_name_in_relation)
	                direction = getattr(field, direction_name)
	                query = query.join(relation_model)
	                query = query.order_by(direction())
	            else:
	                field = getattr(self.model, field_name)
	                direction = getattr(field, direction_name)
	                query = query.order_by(direction())
	    else:
	        pks = primary_key_names(self.model)
	        pk_order = (getattr(self.model, field).asc() for field in pks)
	        query = query.order_by(*pk_order)

	    if self.group_by:
	        for field_name in self.group_by:
	            if '.' in field_name:
	                field_name, field_name_in_relation = field_name.split('.')
	                relation_model = get_related_model(model, field_name)
	                field = getattr(relation_model, field_name_in_relation)
	                query = query.join(relation_model)
	                query = query.group_by(field)
	            else:
	                field = getattr(self.model, field_name)
	                query = query.group_by(field)

	    return query
