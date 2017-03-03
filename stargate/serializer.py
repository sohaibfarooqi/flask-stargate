import re
from sqlalchemy.exc import NoInspectionAvailable
from sqlalchemy.ext.hybrid import HYBRID_PROPERTY
from sqlalchemy import Column
from .proxy import manager_info
from sqlalchemy.inspection import inspect as sqlalchemy_inspect
from datetime import date, datetime, time, timedelta
from .exception import IllegalArgumentError, SerializationException
from .utils import get_relations, get_related_model, parse_expansions
from sqlalchemy.orm import class_mapper
from flask_sqlalchemy import BaseQuery
from .const import PaginationConst, SerializationConst, RelTypeConst, CollectionEvaluationConst, ResourceInfoConst
from .utils import is_like_list, get_pagination_links, get_paginated_url

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

def foreign_keys(model):
    return [column.name for column in foreign_key_columns(model)]

def expand_resource(related_value, fields, serialize_rel = False):
    
    if isinstance(related_value, list):
        related_model = related_value[0]
    else:
        related_model = related_value
    
    serializer = manager_info(ResourceInfoConst.SERIALIZER_FOR, related_model)
    data = serializer(related_value, fields = fields, serialize_rel = False)
    
    pk_id_ = getattr(related_model, manager_info(ResourceInfoConst.PRIMARY_KEY_FOR,related_model))
    self_link = manager_info(ResourceInfoConst.URL_FOR, related_model, pk_id = pk_id_)
    return data, self_link

def create_relationship(model, instance, relation, expand = None):
    EXPAND = True
    fields = None
    
    if expand is None:
        EXPAND = False
    
    else:
        if  relation in expand['expand']:
            pass
        
        else:
            relation_ = [t[0] for t in expand['expand_partial'] if t[0] == relation]
            if relation_:
                for t in expand['expand_partial']: 
                    if t[0] == relation:
                        fields = t[1]
            else:
                EXPAND = False
                

    result = {'meta':{'_links':{}}}
    related_model = get_related_model(model, relation)
    related_value = getattr(instance, relation)
    pagination_links = {}

    pk_value = getattr(instance, manager_info(ResourceInfoConst.PRIMARY_KEY_FOR,model))
    #Lazy Loading
    if isinstance(related_value, BaseQuery):
        related_value_paginated = related_value.paginate(PaginationConst.PAGE_NUMBER, PaginationConst.PAGE_SIZE, error_out=False)
        related_value = related_value_paginated.items
        
        self_link = manager_info(ResourceInfoConst.URL_FOR, model, pk_id = pk_value, relation = relation)
        result['meta']['_links'].update(get_pagination_links(PaginationConst.PAGE_SIZE, PaginationConst.PAGE_NUMBER, related_value_paginated.total, 1, related_value_paginated.pages, related_value_paginated.next_num, related_value_paginated.prev_num , url = self_link))
        self_link = get_paginated_url(self_link, PaginationConst.PAGE_NUMBER, PaginationConst.PAGE_SIZE)
        result['meta']['_links'].update({'self': self_link})
        result['meta']['_type'] = RelTypeConst.TO_MANY
        result['meta']['_evaluation'] = CollectionEvaluationConst.LAZY
        
        if EXPAND:
            result['data'], self_link = expand_resource(related_value, fields, serialize_rel = False)
    
    #Eager Loading
    elif isinstance(related_value, list):
        self_link = manager_info(ResourceInfoConst.URL_FOR, model, pk_id = pk_value, relation = relation)
        result['meta']['_links'].update({'self': self_link})
        result['meta']['_type'] = RelTypeConst.TO_MANY
        result['meta']['_evaluation'] = CollectionEvaluationConst.EAGER

        if EXPAND:
            result['data'], self_link = expand_resource(related_value, fields, serialize_rel = False)
    
    elif related_value is not None:
        
        related_id = getattr(related_value, manager_info(ResourceInfoConst.PRIMARY_KEY_FOR, related_model))
        self_link = manager_info(ResourceInfoConst.URL_FOR, model, pk_id = pk_value, relation = relation, related_id = related_id)
        result['meta']['_type'] = RelTypeConst.TO_ONE
        result['meta']['_links'] = {'self': self_link}
        serializer = manager_info(ResourceInfoConst.SERIALIZER_FOR,related_model)
        
        if EXPAND:
            result['data'], self_link = expand_resource(related_value, fields, serialize_rel = False)
    else:
        result['data'] = {}
    return result

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
                    inspected_instance = sqlalchemy_inspect(model)
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

            pk_name = manager_info(ResourceInfoConst.PRIMARY_KEY_FOR, model)
            
            if fields:
                fields = set(fields)
                fields.add(pk_name)
                columns = [c for c in columns if c in fields]

            if exclude:
                columns = [c for c in columns if c not in fields]
            
            if expand:
                expand = parse_expansions(model, expand)
            
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
        pk_name = manager_info(ResourceInfoConst.PRIMARY_KEY_FOR, model)
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
            result[SerializationConst.ATTRIBUTES] = attributes

        if serialize_rel:
            relations = get_relations(model)
            result[SerializationConst._EMBEDDED] = dict((rel, create_relationship(model, instance, rel, expand = expand))
                                                    for rel in relations)
        return result
