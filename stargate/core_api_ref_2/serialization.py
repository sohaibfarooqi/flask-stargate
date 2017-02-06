# serialization.py - JSON serialization for SQLAlchemy models
from __future__ import division

from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

from flask import request
from sqlalchemy import Column
from sqlalchemy.exc import NoInspectionAvailable
from sqlalchemy.ext.hybrid import HYBRID_PROPERTY
from sqlalchemy.inspection import inspect
from werkzeug.routing import BuildError
from werkzeug.urls import url_quote_plus

from .helpers import collection_name
from .helpers import is_mapped_class
from .helpers import foreign_keys
from .helpers import get_by
from .helpers import get_model
from .helpers import get_related_model
from .helpers import get_relations
from .helpers import has_field
from .helpers import is_like_list
from .helpers import primary_key_for
from .helpers import primary_key_value
from .helpers import serializer_for
from .helpers import strings_to_datetimes
from .helpers import url_for

COLUMN_BLACKLIST = ('_sa_polymorphic_on', )

if hasattr(timedelta, 'total_seconds'):
    def total_seconds(td):
        return td.total_seconds()
else:
    def total_seconds(td):
        secs = td.seconds + td.days * 24 * 3600
        return (td.microseconds + secs * 10**6) / 10**6


class SerializationException(Exception):
    def __init__(self, instance, message=None, resource=None, *args, **kw):
        super(SerializationException, self).__init__(*args, **kw)
        self.resource = resource
        self.message = message
        self.instance = instance


class DeserializationException(Exception):
    
    def __init__(self, *args, **kw):
        super(DeserializationException, self).__init__(*args, **kw)

        self.detail = None

    def message(self):
        base = 'Failed to deserialize object'
        if self.detail is not None:
            return '{0}: {1}'.format(base, self.detail)
        return base


class ClientGeneratedIDNotAllowed(DeserializationException):
    def __init__(self, *args, **kw):
        super(ClientGeneratedIDNotAllowed, self).__init__(*args, **kw)

        self.detail = 'Server does not allow client-generated IDS'


class ConflictingType(DeserializationException):
    def __init__(self, expected_type, given_type, relation_name=None, *args,
                 **kw):
        super(ConflictingType, self).__init__(*args, **kw)

        self.relation_name = relation_name

        self.expected_type = expected_type

        self.given_type = given_type

        if relation_name is None:
            detail = 'expected type "{0}" but got type "{1}"'
            detail = detail.format(expected_type, given_type)
        else:
            detail = ('expected type "{0}" but got type "{1}" in linkage'
                      ' object for relationship "{2}"')
            detail = detail.format(expected_type, given_type, relation_name)
        self.detail = detail


class UnknownField(DeserializationException):
    field_type = None

    def __init__(self, field, *args, **kw):
        super(UnknownField, self).__init__(*args, **kw)

        self.field = field

        self.detail = 'model has no {0} "{1}"'.format(self.field_type, field)


class UnknownRelationship(UnknownField):
    field_type = 'relationship'


class UnknownAttribute(UnknownField):
    field_type = 'attribute'


class MissingInformation(DeserializationException):
    element = None

    def __init__(self, relation_name=None, *args, **kw):
        super(MissingInformation, self).__init__(*args, **kw)

        self.relation_name = relation_name

        if relation_name is None:
            detail = 'missing "{0}" element'
            detail = detail.format(self.element)
        else:
            detail = ('missing "{0}" element in linkage object for'
                      ' relationship "{1}"')
            detail = detail.format(self.element, relation_name)
        self.detail = detail


class MissingData(MissingInformation):
    element = 'data'


class MissingID(MissingInformation):
    element = 'id'


class MissingType(MissingInformation):
    element = 'type'


def get_column_name(column):
    if hasattr(column, '__clause_element__'):
        clause_element = column.__clause_element__()
        if not isinstance(clause_element, Column):
            msg = 'Expected a column attribute of a SQLAlchemy ORM class'
            raise TypeError(msg)
        return clause_element.key
    return column


def create_relationship(model, instance, relation):
    result = {}
    pk_value = primary_key_value(instance)
    self_link = url_for(model, pk_value, relation, relationship=True)
    related_link = url_for(model, pk_value, relation)
    result['links'] = {'self': self_link}
    try:
        related_model = get_related_model(model, relation)
        url_for(related_model)
    except ValueError:
        pass
    else:
        result['links']['related'] = related_link
    related_value = getattr(instance, relation)
    if is_like_list(instance, relation):
        result['data'] = [simple_relationship_serialize(instance)
                          for instance in related_value]
    elif related_value is not None:
        result['data'] = simple_relationship_serialize(related_value)
    else:
        result['data'] = None
    return result


class Serializer(object):
    def __call__(self, instance, only=None):
        raise NotImplementedError


class Deserializer(object):
    def __init__(self, session, model):
        self.session = session
        self.model = model

    def __call__(self, document):
        raise NotImplementedError


class DefaultSerializer(Serializer):
    def __init__(self, only=None, exclude=None, additional_attributes=None,
                 **kw):
        super(DefaultSerializer, self).__init__(**kw)
        if only is not None and exclude is not None:
            raise ValueError('Cannot specify both `only` and `exclude` keyword'
                             ' arguments simultaneously')
        if (additional_attributes is not None and exclude is not None and
                any(attr in exclude for attr in additional_attributes)):
            raise ValueError('Cannot exclude attributes listed in the'
                             ' `additional_attributes` keyword argument')
        if only is not None:
            only = set(get_column_name(column) for column in only)
            only |= set(['type', 'id'])
        if exclude is not None:
            exclude = set(get_column_name(column) for column in exclude)
        self.default_fields = only
        self.exclude = exclude
        self.additional_attributes = additional_attributes

    def __call__(self, instance, only=None):
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
                try:
                    serialize = serializer_for(model_)
                except ValueError:
                    serialize = simple_serialize
                attributes[key] = serialize(val)
        id_ = attributes.pop('id')
        type_ = collection_name(model)
        result = dict(id=id_, type=type_)
        if attributes:
            result['attributes'] = attributes
        if ((self.default_fields is None or 'self' in self.default_fields)
                and (only is None or 'self' in only)):
            instance_id = primary_key_value(instance)
            try:
                path = url_for(model, instance_id, _method='GET')
            except BuildError:
                pass
            else:
                url = urljoin(request.url_root, path)
                result['links'] = dict(self=url)
        pk_name = primary_key_for(model)
        if pk_name != 'id':
            result['id'] = result['attributes'][pk_name]
        if 'id' in result:
            try:
                result['id'] = str(result['id'])
            except UnicodeEncodeError:
                result['id'] = url_quote_plus(result['id'].encode('utf-8'))
        relations = get_relations(model)
        if self.default_fields is not None:
            relations = [r for r in relations if r in self.default_fields]
        if only is not None:
            relations = [r for r in relations if r in only]
        if self.exclude is not None:
            relations = [r for r in relations if r not in self.exclude]
        if not relations:
            return result
        cr = create_relationship
        result['relationships'] = dict((rel, cr(model, instance, rel))
                                       for rel in relations)
        return result


class DefaultRelationshipSerializer(Serializer):
    def __call__(self, instance, only=None, _type=None):
        if _type is None:
            _type = collection_name(get_model(instance))
        return {'id': str(primary_key_value(instance)), 'type': _type}


class DefaultDeserializer(Deserializer):
    def __init__(self, session, model, allow_client_generated_ids=False, **kw):
        super(DefaultDeserializer, self).__init__(session, model, **kw)

        self.allow_client_generated_ids = allow_client_generated_ids

    def __call__(self, document):
        if 'data' not in document:
            raise MissingData
        data = document['data']
        if 'type' not in data:
            raise MissingType
        if 'id' in data and not self.allow_client_generated_ids:
            raise ClientGeneratedIDNotAllowed
        type_ = data.pop('type')
        expected_type = collection_name(self.model)
        if type_ != expected_type:
            raise ConflictingType(expected_type, type_)
        for field in data:
            if field == 'relationships':
                for relation in data['relationships']:
                    if not has_field(self.model, relation):
                        raise UnknownRelationship(relation)
            elif field == 'attributes':
                for attribute in data['attributes']:
                    if not has_field(self.model, attribute):
                        raise UnknownAttribute(attribute)
        links = {}
        if 'relationships' in data:
            links = data.pop('relationships', {})
            for link_name, link_object in links.items():
                if 'data' not in link_object:
                    raise MissingData(link_name)
                linkage = link_object['data']
                related_model = get_related_model(self.model, link_name)
                expected_type = collection_name(related_model)
                DRD = DefaultRelationshipDeserializer
                deserialize = DRD(self.session, related_model, link_name)
                links[link_name] = deserialize(linkage)
        pass
        data.update(data.pop('attributes', {}))
        data = strings_to_datetimes(self.model, data)
        instance = self.model(**data)
        for relation_name, related_value in links.items():
            setattr(instance, relation_name, related_value)
        return instance


class DefaultRelationshipDeserializer(Deserializer):
    def __init__(self, session, model, relation_name=None):
        super(DefaultRelationshipDeserializer, self).__init__(session, model)
        self.model = model

        self.type_name = collection_name(self.model)

        self.relation_name = relation_name

    def __call__(self, data):
        if not isinstance(data, list):
            if 'id' not in data:
                raise MissingID(self.relation_name)
            if 'type' not in data:
                raise MissingType(self.relation_name)
            type_ = data['type']
            if type_ != self.type_name:
                raise ConflictingType(self.relation_name, self.type_name,
                                      type_)
            id_ = data['id']
            return get_by(self.session, self.model, id_)
        return list(map(self, data))


simple_serialize = DefaultSerializer()


simple_relationship_serialize = DefaultRelationshipSerializer()
