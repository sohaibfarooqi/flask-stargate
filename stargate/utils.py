"""Various utility functions used across application. Refer to individual function docs for more details.

"""

import datetime
import re
import math
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.orm.exc import NoResultFound
from .exception import StargateException, ResourceNotFound
from .proxy import manager_info
from .const import ResourceInfoConst
from sqlalchemy import inspect as sqlalchemy_inspect
from dateutil.parser import parse as parse_datetime
from sqlalchemy.sql.expression import ColumnElement
from sqlalchemy.ext.associationproxy import AssociationProxy
from sqlalchemy.orm import RelationshipProperty as RelProperty
from sqlalchemy import Date, DateTime, Interval, Time
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm import RelationshipProperty as RelProperty
from sqlalchemy.ext.associationproxy import AssociationProxy
from sqlalchemy.inspection import inspect
from flask import request

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

	pk_name = manager_info(ResourceInfoConst.PRIMARY_KEY_FOR, model)
		
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

	CURRENT_TIME_MARKERS = ('CURRENT_TIMESTAMP', 'CURRENT_DATE', 'LOCALTIMESTAMP')
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

def get_pagination_links(page_size, page_number, num_results, first, last, next, prev, url = None):

	if url is not None:
		link_url =  url	

	else:
		query_params = request.args
		new_query = dict((k, v) for k, v in query_params.items()
							if k not in ('page_number', 'page_size'))
		new_query_string = '&'.join(map('='.join, new_query.items()))
		link_url =  '{0}?{1}'.format(request.base_url, new_query_string)

	if num_results == 0:
		last = 1

	else:
		last = int(math.ceil(num_results / page_size))

	prev = page_number - 1 if page_number > 1 else None
	next = page_number + 1 if page_number < last else None

	first = get_paginated_url(link_url,first,page_size)
	last = get_paginated_url(link_url,last,page_size)

	if next is not None:
		next = get_paginated_url(link_url,next,page_size)

	if prev is not None:
		prev = get_paginated_url(link_url,prev,page_size)

	return {'first': first, 'last': last, 'next': next, 'prev': prev}


def get_paginated_url(link, page_number, page_size):

	if link.endswith('?'):
		return "{0}page_number={1}&page_size={2}".format(link, page_number, page_size)

	elif "?" in link and not link.endswith('?'):
		return "{0}&page_number={1}&page_size={2}".format(link, page_number, page_size)
	
	else:
		return "{0}?page_number={1}&page_size={2}".format(link, page_number, page_size)


def get_relations(model):
		NON_RELATION_ATTRS = ('query', 'query_class', '_sa_class_manager','_decl_class_registry')
		return [k for k in dir(model) if not (k.startswith('__') or k in NON_RELATION_ATTRS) and get_related_model(model, k)]
	
def get_related_model(model, relationname):

	if hasattr(model, relationname):
		attr = getattr(model, relationname)
	if hasattr(attr, 'property') and isinstance(attr.property, RelProperty):
		return attr.property.mapper.class_
	if isinstance(attr, AssociationProxy):
		return get_related_association_proxy_model(attr)
	return None

def get_related_association_proxy_model(attr):
	prop = attr.remote_attr.property
	for attribute in ('mapper', 'parent'):
		if hasattr(prop, attribute):
			return getattr(prop, attribute).class_
	return None       


def parse_expansions(model, expand):
	REGEX_MATCH_FIELD = r'((\w+)\(([\s+\w\s+,\s+.]+)\))'
	nested_fields = re.findall(REGEX_MATCH_FIELD, expand)

	resource = expand
	resource = re.sub(REGEX_MATCH_FIELD, '', resource)
	resource = re.sub(r'\s+', '', resource)
	resource = re.sub(r'\A(?:\s+)?,(?:\s+)?', '', resource)
	resource = re.sub(r'(?:\s+)?,(?:\s+)?$', '', resource)
	resource = resource.split(',')
	expand_full = set(resource)

	all_relations = get_relations(model)
	all_joins = set()
	expand_partial = list()
	for fields in nested_fields:
		if fields[1] in all_relations:
			nested_resource_fields = [field.strip() for field in fields[2].split(',') if field is not None]
			resource_fields = set(nested_resource_fields)
			expand_partial.append((fields[1], resource_fields))
	return dict(expand = expand_full, expand_partial = expand_partial)

