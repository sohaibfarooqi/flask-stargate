import datetime
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.orm.exc import NoResultFound
from .exception import StargateException
from .proxy import manager_info, PRIMARY_KEY_FOR
from sqlalchemy import inspect as sqlalchemy_inspect
from dateutil.parser import parse as parse_datetime
from sqlalchemy.sql.expression import ColumnElement
from sqlalchemy.ext.associationproxy import AssociationProxy
from sqlalchemy.orm import RelationshipProperty as RelProperty
from sqlalchemy import Date, DateTime, Interval, Time

CURRENT_TIME_MARKERS = ('CURRENT_TIMESTAMP', 'CURRENT_DATE', 'LOCALTIMESTAMP')

def session_query(session, model):
	if hasattr(model, 'query'):
		if callable(model.query):
			query = model.query()
		else:
			query = model.query
		if hasattr(query, 'filter'):
			return query
	return session.query(model)

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

def get_resource(session, model, pk_id):

	pk_name = manager_info(PRIMARY_KEY_FOR, model)
		
	try:
		query = session_query(session, model)
		query = query.filter(getattr(model, pk_name) == pk_id)
		resource = query.first()
		return resource
	except NoResultFound as exception:
		detail = 'No result found'
		raise ResourceNotFound(model.__name__(), id = pk_name, msg=detail)

	except MultipleResultsFound as exception:
		detail = 'Multiple results found'
		raise StargateException(msg=detail)

def has_field(model, fieldname):
    descriptors = sqlalchemy_inspect(model).all_orm_descriptors._data
    if fieldname in descriptors and hasattr(descriptors[fieldname], 'fset'):
        return descriptors[fieldname].fset is not None
    return hasattr(model, fieldname)

def get_field_type(model, fieldname):
    field = getattr(model, fieldname)
    if isinstance(field, ColumnElement):
        return field.type
    if isinstance(field, AssociationProxy):
        field = field.remote_attr
    if hasattr(field, 'property'):
        prop = field.property
        if isinstance(prop, RelProperty):
            return None
        return prop.columns[0].type
    return None

def string_to_datetime(model, fieldname, value):
    if value is None:
        return value
    field_type = get_field_type(model, fieldname)
    if isinstance(field_type, (Date, Time, DateTime)):
        if value.strip() == '':
            return None
        if value in CURRENT_TIME_MARKERS:
            return getattr(func, value.lower())()
        value_as_datetime = parse_datetime(value)
        if isinstance(field_type, Date):
            return value_as_datetime.date()
        if isinstance(field_type, Time):
            return value_as_datetime.timetz()
        return value_as_datetime
    if isinstance(field_type, Interval) and isinstance(value, int):
        return datetime.timedelta(seconds=value)
    return value