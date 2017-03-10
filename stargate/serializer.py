"""Default serializer class for API. Supports instance and collection serialization. Provide options
like resource expansion, field selection, field exclusion and skip relationship serialization.

"""

import re
from sqlalchemy.exc import NoInspectionAvailable
from sqlalchemy.ext.hybrid import HYBRID_PROPERTY
from sqlalchemy import Column
from .resource_info import resource_info
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
    
    serializer = resource_info(ResourceInfoConst.SERIALIZER, related_model)
    data = serializer(related_value, fields = fields, serialize_rel = False)
    
    pk_id_ = getattr(related_model, resource_info(ResourceInfoConst.PRIMARY_KEY,related_model))
    self_link = resource_info(ResourceInfoConst.URL, related_model, pk_id = pk_id_)
    return data, self_link

def serialize_relationship(model, instance, relation, expand = None):
    """Relation serializer function. This method is called from _serialize_one() on all the 
    relations of object.

    :param model: Resource model class.
    :param instance: Primary resource.
    :param relation: relation name.
    :param expand: Parsed list of resource that need to be expanded.
        
    """
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
                

    result = {}
    related_model = get_related_model(model, relation)
    related_value = getattr(instance, relation)
    pagination_links = {}

    pk_value = getattr(instance, resource_info(ResourceInfoConst.PRIMARY_KEY,model))
    #Lazy Loading
    if isinstance(related_value, BaseQuery):
        related_value_paginated = related_value.paginate(PaginationConst.PAGE_NUMBER, PaginationConst.PAGE_SIZE, error_out=False)
        related_value = related_value_paginated.items
        if related_value:
            self_link = resource_info(ResourceInfoConst.URL, model, pk_id = pk_value, relation = relation)
            result['meta'] = {}
            result['meta']['_links'] = get_pagination_links(PaginationConst.PAGE_SIZE, PaginationConst.PAGE_NUMBER, related_value_paginated.total, 1, related_value_paginated.pages, related_value_paginated.next_num, related_value_paginated.prev_num , url = self_link)
            self_link = get_paginated_url(self_link, PaginationConst.PAGE_NUMBER, PaginationConst.PAGE_SIZE)
            result['meta']['_links'].update({'self': self_link})
            result['meta']['_type'] = RelTypeConst.TO_MANY
            result['meta']['_evaluation'] = CollectionEvaluationConst.LAZY
            
            if EXPAND:
                result['data'], self_link = expand_resource(related_value, fields, serialize_rel = False)
    
    #Eager Loading
    elif isinstance(related_value, list):
        if related_value:
            self_link = resource_info(ResourceInfoConst.URL, model, pk_id = pk_value, relation = relation)
            result['meta'] = {}
            result['meta']['_links'] = {'self': self_link}
            result['meta']['_type'] = RelTypeConst.TO_MANY
            result['meta']['_evaluation'] = CollectionEvaluationConst.EAGER

            if EXPAND:
                result['data'], self_link = expand_resource(related_value, fields, serialize_rel = False)
    
    #Single Instance.
    elif related_value is not None:
        
        related_id = getattr(related_value, resource_info(ResourceInfoConst.PRIMARY_KEY, related_model))
        self_link = resource_info(ResourceInfoConst.URL, model, pk_id = pk_value, relation = relation, related_id = related_id)
        result['meta'] = {}
        result['meta']['_type'] = RelTypeConst.TO_ONE
        result['meta']['_links'] = {'self': self_link}
        serializer = resource_info(ResourceInfoConst.SERIALIZER,related_model)
        
        if EXPAND:
            result['data'], self_link = expand_resource(related_value, fields, serialize_rel = False)
    else:
        result['data'] = {}
    return result

#####################################################################################################

class Serializer():
    """Application Default serialization class. Each resource regsiter its own copy of this class 
    during initilization in :class:`~stargate.manager.Manager`. Raise exception of type 
    :class:`~stargate.exception.IllegalArgumentError` if both `fields` and `exclude` key word arguments
    are not None 

    :param model: SQLALchemy model.
    :param primary_key: Primary key column for model.
    :param fields: Resource attributes to be serialized. By default all attributes will be seriaized.
    :param exclude: Exclude resource attributes from serialization.

    This class can be used globally within stargate package. Example usage of this class:
    #Return User serialization class

    .. code-block:: python
        
        serializer = resource_info(ResourceInfoConst.SERIALIZER, User)
        data = serializer(data)

    """
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
        """Callable for Serializer class. Can serialize list and single instance of SQLAlchemy 
        resutlset objects.
        
        Example:

        .. code-block:: python
        
            serializer = resource_info(ResourceInfoConst.SERIALIZER, User)
            #This execute callable.
            data = serializer(data)

        :param result_set: List or single insance of SQLALchemy resuit set.
        :param fields: Resource attributes to be serialized.
        :param exclude: Resource attributes to be exluded from serialized.
        :param expand: Exclude resource attributes from serialization.
        :param serialize_rel: Boolean for serializing related resources.

        """
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

            pk_name = resource_info(ResourceInfoConst.PRIMARY_KEY, model)
            
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
        """Called internally from __call__ if list of object need to be serialized
        
        :param columns: Resource database table columns.
        :param result_set: Objects needs to be serilized.
        :param expand: List of relations need to be expanded.
        :param serialize_rel: Boolean for serializing related resources.
        
        """
        result = []
        for instance in result_set:
            try:
                serialized = self._serialize_one(columns, instance, expand = expand, serialize_rel = serialize_rel)
                result.append(serialized)
            except SerializationException as exception:
                raise SerializationException(instance, str(exception))
        return result

    def _serialize_one(self, columns, instance, expand = None, serialize_rel = None):
        """Called internally from __call__ if single object need to be serialized
        
        :param columns: Resource database table columns.
        :param instance: Object needs to be serilized.
        :param expand: List of relations need to be expanded.
        :param serialize_rel: Boolean for serializing related resources.
        
        """
        result = {}
        
        try:
            model = type(instance)
            pk_name = resource_info(ResourceInfoConst.PRIMARY_KEY, model)
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
                result['_link'] = resource_info(ResourceInfoConst.URL, model, pk_id = result[pk_name])
            
            if serialize_rel:
                relations = get_relations(model)
                result[SerializationConst.EMBEDDED] = dict((rel, serialize_relationship(model, instance, rel, expand = expand))
                                                        for rel in relations)
            return result
            
        except SerializationException as exception:
            raise SerializationException(instance, str(exception))