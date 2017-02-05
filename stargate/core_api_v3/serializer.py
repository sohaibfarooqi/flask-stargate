import re
from sqlalchemy.inspection import inspect
from sqlalchemy.exc import NoInspectionAvailable
from urllib.parse import urljoin
from sqlalchemy.ext.hybrid import HYBRID_PROPERTY
from sqlalchemy import Column
from .proxy import url_for, serializer_for, primary_key_for, collection_name_for, model_for
from sqlalchemy.inspection import inspect as sqlalchemy_inspect
from datetime import date, datetime, time, timedelta
from werkzeug.routing import BuildError
from flask import request
from .exception import IllegalArgumentError, ResourceNotFound, SerializationException
from .views.query_helper.inclusion import Inclusions

COLUMN_BLACKLIST = ('_sa_polymorphic_on', )

RELATION_BLACKLIST = ('query', 'query_class', '_sa_class_manager',
                      '_decl_class_registry')

REGEX_MATCH_FIELD = r'((\w+)\(([\s+\w\s+,\s+.]+)\))'

"""Serialization Helper Methods"""
def get_column_name(column):
    if hasattr(column, '__clause_element__'):
        clause_element = column.__clause_element__()
        if not isinstance(clause_element, Column):
            msg = 'Expected a column attribute of a SQLAlchemy ORM class'
            raise IllegalArgumentError(msg)
        return clause_element.key
    return column

def is_mapped_class(cls):
    try:
        sqlalchemy_inspect(cls)
        return True
    except NoInspectionAvailable:
        return False
        
def get_model(instance):
    return type(instance)

def foreign_key_columns(model):
    try:
        inspector = sqlalchemy_inspect(model)
    except NoInspectionAvailable:
        inspector = class_mapper(model)
    all_columns = inspector.columns
    return [c for c in all_columns if c.foreign_keys]

def create_relationship(model, instance, relation, expand = False):
    result = {'meta':{}}
    related_model = Inclusions.get_related_model(model, relation)
    related_value = getattr(instance, relation)
    
    pk_value = getattr(instance, primary_key_for(model))

    if is_like_list(instance, relation):
        related_value = related_value.all()
        related_class = related_value[0].__class__
        nested_url = url_for(model, pk_id = pk_value, relation = relation)
        result['meta']['_links'] = {'self': nested_url, 'next': nested_url, 'prev': nested_url, 'first': nested_url, 'last': nested_url}
        result['meta']['_type'] = 'TO_MANY'
        serializer = serializer_for(related_class)
        result['data'] = serializer(related_value, serialize_rel = False)

        pk_id_ = getattr(related_value[0], primary_key_for(related_class))
        self_link = url_for(related_model, pk_id = pk_id_)
        result['data'][0]['_link'] = dict(self = self_link)
    
    elif related_value is not None:
        related_id = getattr(related_value, primary_key_for(related_model))
        nested_url = url_for(model, pk_id = pk_value, relation = relation, related_id = related_id)
        result['meta']['_type'] = 'TO_ONE'
        result['meta']['_links'] = {'self': nested_url}
        serializer = serializer_for(related_model)
        result['data'] = serializer(related_value, serialize_rel = False)
        pk_id_ = getattr(related_value, primary_key_for(related_model))
        self_link = url_for(related_model, pk_id = pk_id_)
        result['data']['_link'] = dict(self = self_link)
    else:
        result['data'] = None
    return result

def foreign_keys(model):
    return [column.name for column in foreign_key_columns(model)]

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

def primary_key_value(instance, as_string=False):
    result = getattr(instance, primary_key_for(instance))
    if not as_string:
        return result
    try:
        return str(result)
    except UnicodeEncodeError:
        return url_quote_plus(result.encode('utf-8'))

def parse_field_set(field_str):
    
    resource_fields = re.sub(REGEX_MATCH_FIELD, '', field_str)
    resource_fields = re.sub(r'\s+', '', resource_fields)
    resource_fields = re.sub(r'\A(?:\s+)?,(?:\s+)?', '', resource_fields)
    resource_fields = re.sub(r'(?:\s+)?,(?:\s+)?$', '', resource_fields)
    resource_fields = resource_fields.split(',')

    return set(resource_fields)
#####################################################################################################

class Serializer(object):
    def __call__(self, instance, only=None):
        raise NotImplementedError

class DefaultSerializer():

    def __init__(self, model, fields = None, exclude = None, expand = None):
        
        self.model = model
        
        if fields is not None and exclude is not None:
            raise IllegalArgumentError('Cannot specify both `fields` and `exclude` keyword'
                             ' arguments simultaneously')
        if fields is not None:
            fields = set(get_column_name(column) for column in fields)
            pk_name = primary_key_for(self.model)
            include.add(pk_name)
        
        if exclude is not None:
            exclude = set(get_column_name(column) for column in exclude)
        
        self.allowed_fields = fields
        self.exclude = exclude
    
    def __call__(self, instance, fields = None, exclude = None, expand = None, serialize_rel = True):
        
        if isinstance(instance, list):
            return self._serialize_many(instance, fields = fields, exclude = exclude, expand = expand, serialize_rel = serialize_rel)
        
        else:
            return self._serialize_one(instance, fields = fields, exclude = exclude, expand = expand, serialize_rel = serialize_rel)

    def _serialize_many(self, instances, fields = None, exclude = None, expand = None, serialize_rel = False):
        result = []
        for instance in instances:
            model = get_model(instance)
            try:
                serialized = self._serialize_one(instance, fields = fields, exclude = exclude, expand = expand, serialize_rel = serialize_rel)
                result.append(serialized)
            except SerializationException as exception:
                raise SerializationException(instance,str(exception))
        return result

    def _serialize_one(self, instance, fields = None, exclude = None, expand = None, serialize_rel = None):
        
        result = {}
        columns = set()
        if fields  and exclude:
            raise IllegalArgumentError('Cannot specify both `fields` and `exclude` keyword'
                             ' arguments simultaneously')
        if self.allowed_fields:
            columns = self.allowed_fields
        
        else:
            model = type(instance)
            try:
                inspected_instance = inspect(model)
            except NoInspectionAvailable:
                return instance
            column_attrs = inspected_instance.column_attrs.keys()
            descriptors = inspected_instance.all_orm_descriptors.items()
            hybrid_columns = [k for k, d in descriptors if d.extension_type == HYBRID_PROPERTY]
            columns = column_attrs + hybrid_columns
            foreign_key_columns = foreign_keys(model)
            columns = (c for c in columns if c not in foreign_key_columns)
            
        if self.exclude:
                columns = (c for c in columns if c not in self.exclude)

        pk_name = primary_key_for(model)
        
        if fields:
            fields = parse_field_set(include)
            fields.add(pk_name)
            columns = (c for c in columns if c in fields)

        if exclude:
            fields = parse_field_set(exclude)
            columns = (c for c in columns if c not in fields)
        
        attributes = dict((column, getattr(instance, column))
                          for column in columns)
        attributes = dict((k, (v() if callable(v) else v))
                          for k, v in attributes.items())
        for key, val in attributes.items():
            if isinstance(val, (date, datetime, time)):
                attributes[key] = val.isoformat()
            elif isinstance(val, timedelta):
                attributes[key] = total_seconds(val)
        
        if attributes:
            result[pk_name] = attributes.pop(pk_name)
            result['attributes'] = attributes
        
        if serialize_rel:
            relations = Inclusions.get_relations(model)
            print(relations)
            cr = create_relationship
            result['_embedded'] = dict((rel, cr(model, instance, rel))
                                       for rel in relations)
        return result