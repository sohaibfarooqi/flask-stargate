from sqlalchemy.inspection import inspect
from sqlalchemy.exc import NoInspectionAvailable
from urllib.parse import urljoin
from sqlalchemy.ext.hybrid import HYBRID_PROPERTY
from .proxy import url_for, serializer_for, primary_key_for, collection_name_for, model_for
from sqlalchemy.inspection import inspect as sqlalchemy_inspect
from datetime import date, datetime, time, timedelta
from werkzeug.routing import BuildError
from flask import request
from .exception import IllegalArgumentError, ResourceNotFound, SerializationException

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


def foreign_keys(model):
    return [column.name for column in foreign_key_columns(model)]

def primary_key_value(instance, as_string=False):
    result = getattr(instance, primary_key_for(instance))
    if not as_string:
        return result
    try:
        return str(result)
    except UnicodeEncodeError:
        return url_quote_plus(result.encode('utf-8'))
#####################################################################################################

class Serializer(object):
    def __call__(self, instance, only=None):
        raise NotImplementedError


class DefaultSerializer(Serializer):
    def __init__(self, only=None, exclude=None, additional_attributes=None,
                 **kw):
        super(DefaultSerializer, self).__init__(**kw)
        if only is not None and exclude is not None:
            raise IllegalArgumentError('Cannot specify both `only` and `exclude` keyword'
                             ' arguments simultaneously')
        if (additional_attributes is not None and exclude is not None and
                any(attr in exclude for attr in additional_attributes)):
            raise IllegalArgumentError('Cannot exclude attributes listed in the'
                             ' `additional_attributes` keyword argument')
        if only is not None:
            only = set(get_column_name(column) for column in only)
            only |= set(['type', 'id'])
        if exclude is not None:
            exclude = set(get_column_name(column) for column in exclude)
        self.default_fields = only
        self.exclude = exclude
        self.additional_attributes = additional_attributes
    
    def __call__(self, instance, only = None, many = False):
        
        if many and isinstance(instance, list):
            self._serialize_many(instance, only = None)
        
        else:
            self._serialize_one(instance, only=None)

    def _serialize_many(self, instances, only=None):
        result = []
        for instance in instances:
            model = get_model(instance)
            serialize = serializer_for(model)
            serialize = self.serialize
            _type = collection_name_for(model)
            try:
                serialized = self._serialize_one(instance, only=only)
                result.append(serialized)
            except SerializationException as exception:
                raise SerializationException(instance,str(exception))
        return result

    def _serialize_one(self, instance, only=None):
        if only is not None:
            only = set(only) | set(['type', 'id'])
        model = type(instance)
        try:
            inspected_instance = inspect(model)
        except NoInspectionAvailable:
            return instance
        column_attrs = inspected_instance.column_attrs.keys()
        descriptors = inspected_instance.all_orm_descriptors.items()
        hybrid_columns = [k for k, d in descriptors
                          if d.extension_type == HYBRID_PROPERTY]
        columns = column_attrs + hybrid_columns
        if self.additional_attributes is not None:
            columns += self.additional_attributes

        if self.default_fields is not None:
            columns = (c for c in columns if c in self.default_fields)
        if only is not None:
            columns = (c for c in columns if c in only)

        if self.exclude is not None:
            columns = (c for c in columns if c not in self.exclude)
        columns = (c for c in columns
                   if not c.startswith('__') and c not in COLUMN_BLACKLIST)
        foreign_key_columns = foreign_keys(model)
        columns = (c for c in columns if c not in foreign_key_columns)

        attributes = dict((column, getattr(instance, column))
                          for column in columns)
        attributes = dict((k, (v() if callable(v) else v))
                          for k, v in attributes.items())
        for key, val in attributes.items():
            if isinstance(val, (date, datetime, time)):
                attributes[key] = val.isoformat()
            elif isinstance(val, timedelta):
                attributes[key] = total_seconds(val)
        for key, val in attributes.items():
            if is_mapped_class(type(val)):
                model_ = get_model(val)
                serialize = serializer_for(model_)
                attributes[key] = serialize(val)
        id_ = attributes.pop('id')
        type_ = collection_name_for(model)
        result = dict(id=id_, type=type_)
        if attributes:
            result['attributes'] = attributes
        if ((self.default_fields is None or 'self' in self.default_fields)
                and (only is None or 'self' in only)):
            instance_id = primary_key_value(instance)
            path = url_for(model, instance_id, _method='GET')
        else:
            url = urljoin(request.url_root, path)
            result['links'] = dict(self=url)
        pk_name = primary_key_for(model)
        if pk_name != 'id':
            result['id'] = result['attributes'][pk_name]
        try:
            result['id'] = str(result['id'])
        except UnicodeEncodeError:
            result['id'] = url_quote_plus(result['id'].encode('utf-8'))

        return result