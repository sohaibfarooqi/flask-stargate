import re
from sqlalchemy.inspection import inspect
from sqlalchemy.exc import NoInspectionAvailable
from urllib.parse import urljoin
from sqlalchemy.ext.hybrid import HYBRID_PROPERTY
from sqlalchemy import Column
from .proxy import manager_info, URL_FOR, SERIALIZER_FOR, PRIMARY_KEY_FOR
from sqlalchemy.inspection import inspect as sqlalchemy_inspect
from datetime import date, datetime, time, timedelta
from werkzeug.routing import BuildError
from flask import request
from .exception import IllegalArgumentError, ResourceNotFound, SerializationException
from .query_helper.inclusion import Inclusions

COLUMN_BLACKLIST = ('_sa_polymorphic_on', )

RELATION_BLACKLIST = ('query', 'query_class', '_sa_class_manager',
                      '_decl_class_registry')

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

def create_relationship(model, instance, relation, expand = None):
    EXPAND = True
    fields = None
    
    if expand is None:
        EXPAND = False
    
    else:
        if  relation in expand['expand_full']:
            pass
        
        else:
            relation_ = [t[0] for t in expand['expand_partial'] if t[0] == relation]
            if relation_:
                for t in expand['expand_partial']: 
                    if t[0] == relation:
                        fields = t[1]
            else:
                EXPAND = False
                

    result = {'meta':{}}
    related_model = Inclusions.get_related_model(model, relation)
    related_value = getattr(instance, relation)
    
    pk_value = getattr(instance, manager_info(PRIMARY_KEY_FOR,model))
    if is_like_list(instance, relation):
        related_class = related_value[0].__class__
        nested_url = manager_info(URL_FOR, model, pk_id = pk_value, relation = relation)
        result['meta']['_links'] = {'self': nested_url, 'next': nested_url, 'prev': nested_url, 'first': nested_url, 'last': nested_url}
        result['meta']['_type'] = 'TO_MANY'
        if EXPAND:
            serializer = manager_info(SERIALIZER_FOR, related_class)
            result['data'] = serializer(related_value, fields = fields, serialize_rel = False)

            pk_id_ = getattr(related_value[0], manager_info(PRIMARY_KEY_FOR,related_class))
            self_link = manager_info(URL_FOR, related_model, pk_id = pk_id_)
            result['data'][0]['_link'] = dict(self = self_link)
    
    elif related_value is not None:
        related_id = getattr(related_value, manager_info(PRIMARY_KEY_FOR,related_model))
        nested_url = manager_info(URL_FOR, model, pk_id = pk_value, relation = relation, related_id = related_id)
        result['meta']['_type'] = 'TO_ONE'
        result['meta']['_links'] = {'self': nested_url}
        serializer = manager_info(SERIALIZER_FOR,related_model)
        if EXPAND:
            result['data'] = serializer(related_value, fields = fields, serialize_rel = False)
            pk_id_ = getattr(related_value, primary_key_for(related_model))
            self_link = manager_info(URL_FOR, related_model, pk_id = pk_id_)
            result['data']['_link'] = dict(self = self_link)
    else:
        result['data'] = {}
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
    result = getattr(instance, manager_info(PRIMARY_KEY_FOR, instance))
    if not as_string:
        return result
    try:
        return str(result)
    except UnicodeEncodeError:
        return url_quote_plus(result.encode('utf-8'))

#####################################################################################################

class Serializer():

    def __init__(self, model, primary_key, fields = None, exclude = None):
        
        self.model = model
        
        if fields is not None and exclude is not None:
            raise IllegalArgumentError('Cannot specify both `fields` and `exclude` keyword'
                             ' arguments simultaneously')
        if fields is not None:
            fields = set(get_column_name(column) for column in fields)
            fields.add(primary_key)
        
        if exclude is not None:
            exclude = set(get_column_name(column) for column in exclude)
        
        self.allowed_fields = fields
        self.exclude = exclude
    
    def __call__(self, result_set, fields = None, exclude = None, expand = None, serialize_rel = True):

        if result_set:
            instance = result_set[0] if isinstance(result_set, list) else result_set
            model = type(instance)
        
            columns = set()
            
            if fields  and exclude:
                raise IllegalArgumentError('Cannot specify both `fields` and `exclude` keyword'
                                 ' arguments simultaneously')
            if self.allowed_fields:
                columns = self.allowed_fields
            
            else:
                try:
                    inspected_instance = inspect(model)
                except NoInspectionAvailable:
                    raise IllegalArgumentError(msg="No inspection available for class{0}".format(model.__class__))
                column_attrs = inspected_instance.column_attrs.keys()
                descriptors = inspected_instance.all_orm_descriptors.items()
                hybrid_columns = [k for k, d in descriptors if d.extension_type == HYBRID_PROPERTY]
                columns = column_attrs + hybrid_columns
                foreign_key_columns = foreign_keys(model)
                columns = [c for c in columns if c not in foreign_key_columns]
                
            if self.exclude:
                columns = [c for c in columns if c not in self.exclude]

            pk_name = manager_info(PRIMARY_KEY_FOR, model)
            
            if fields:
                fields.add(pk_name)
                columns = [c for c in columns if c in fields]

            if exclude:
                columns = [c for c in columns if c not in fields]
            
            if expand:
                expand = Inclusions.parse_expansions(model, expand)
            
            if isinstance(result_set, list):
                return self._serialize_many(columns, result_set, expand = expand, serialize_rel = serialize_rel)
            
            else:
                return self._serialize_one(columns, result_set, expand = expand, serialize_rel = serialize_rel)
        else:
            return None

    def _serialize_many(self, columns, result_set, expand = None, serialize_rel = False):

        result = []
        for instance in result_set:
            try:
                serialized = self._serialize_one(columns, instance, expand = expand, serialize_rel = serialize_rel)
                result.append(serialized)
            except SerializationException as exception:
                raise SerializationException(instance,str(exception))
        return result

    def _serialize_one(self, columns, instance, expand = None, serialize_rel = None):

        result = {}
        model = get_model(instance)
        pk_name = manager_info(PRIMARY_KEY_FOR, model)
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
            cr = create_relationship
            result['_embedded'] = dict((rel, cr(model, instance, rel, expand = expand))
                                       for rel in relations)
        return result
