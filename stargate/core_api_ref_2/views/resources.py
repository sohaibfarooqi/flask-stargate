from flask import json
from flask import request
from werkzeug.exceptions import BadRequest

from ..helpers import collection_name
from ..helpers import get_by
from ..helpers import get_related_model
from ..helpers import has_field
from ..helpers import is_like_list
from ..helpers import primary_key_value
from ..helpers import strings_to_datetimes
from ..serialization import ClientGeneratedIDNotAllowed
from ..serialization import ConflictingType
from ..serialization import DeserializationException
from ..serialization import SerializationException
from .base import APIBase
from .base import error
from .base import error_response
from .base import errors_from_serialization_exceptions
from .base import errors_response
from .base import JSONAPI_VERSION
from .base import MultipleExceptions
from .base import SingleKeyError
from .helpers import changes_on_update


class API(APIBase):

    def __init__(self, *args, **kw):
        super(API, self).__init__(*args, **kw)

        self.changes_on_update = changes_on_update(self.model)

    def collection_processor_type(self, is_relation=False, **kw):
        return 'TO_MANY_RELATION' if is_relation else 'COLLECTION'

    def resource_processor_type(self, is_relation=False,
                                is_related_resource=False, **kw):
        if is_relation:
            if is_related_resource:
                return 'RELATED_RESOURCE'
            return 'TO_ONE_RELATION'
        return 'RESOURCE'

    def _get_related_resource(self, resource_id, relation_name,
                              related_resource_id):
        for preprocessor in self.preprocessors['GET_RELATED_RESOURCE']:
            temp_result = preprocessor(resource_id=resource_id,
                                       relation_name=relation_name,
                                       related_resource_id=related_resource_id)
            if temp_result is not None:
                if isinstance(temp_result, tuple):
                    if len(temp_result) == 2:
                        resource_id, relation_name = temp_result
                    else:
                        resource_id, relation_name, related_resource_id = \
                            temp_result
                else:
                    resource_id = temp_result
        primary_resource = get_by(self.session, self.model, resource_id,
                                  self.primary_key)
        if primary_resource is None:
            detail = 'No instance with ID {0}'.format(resource_id)
            return error_response(404, detail=detail)
        related_model = get_related_model(self.model, relation_name)
        if related_model is None:
            detail = 'No such relation: {0}'.format(relation_name)
            return error_response(404, detail=detail)
        if not is_like_list(primary_resource, relation_name):
            detail = ('Cannot access a related resource by ID from a to-one'
                      ' relation')
            return error_response(404, detail=detail)
        resources = getattr(primary_resource, relation_name)
        primary_keys = (primary_key_value(resource, as_string=True)
                        for resource in resources)
        if not any(k == str(related_resource_id) for k in primary_keys):
            detail = 'No related resource with ID {0}'
            detail = detail.format(related_resource_id)
            return error_response(404, detail=detail)
        resource = get_by(self.session, related_model, related_resource_id)
        return self._get_resource_helper(resource,
                                         primary_resource=primary_resource,
                                         relation_name=relation_name,
                                         related_resource=True)

    def _get_relation(self, resource_id, relation_name):
        try:
            filters, sort, group_by, single = self._collection_parameters()
        except (TypeError, ValueError, OverflowError) as exception:
            detail = 'Unable to decode filter objects as JSON list'
            return error_response(400, cause=exception, detail=detail)
        except SingleKeyError as exception:
            detail = 'Invalid format for filter[single] query parameter'
            return error_response(400, cause=exception, detail=detail)

        for preprocessor in self.preprocessors['GET_RELATION']:
            temp_result = preprocessor(resource_id=resource_id,
                                       relation_name=relation_name,
                                       filters=filters, sort=sort,
                                       group_by=group_by, single=single)
            if temp_result is not None:
                if isinstance(temp_result, tuple) and len(temp_result) == 2:
                    resource_id, relation_name = temp_result
                else:
                    resource_id = temp_result

        primary_resource = get_by(self.session, self.model, resource_id,
                                  self.primary_key)
        if primary_resource is None:
            detail = 'No resource with ID {0}'.format(resource_id)
            return error_response(404, detail=detail)
        related_model = get_related_model(self.model, relation_name)
        if related_model is None:
            detail = 'No such relation: {0}'.format(relation_name)
            return error_response(404, detail=detail)
        if is_like_list(primary_resource, relation_name):
            return self._get_collection_helper(resource=primary_resource,
                                               relation_name=relation_name,
                                               filters=filters, sort=sort,
                                               group_by=group_by,
                                               single=single)
        else:
            resource = getattr(primary_resource, relation_name)
            return self._get_resource_helper(resource=resource,
                                             primary_resource=primary_resource,
                                             relation_name=relation_name)

    def _get_resource(self, resource_id):
        for preprocessor in self.preprocessors['GET_RESOURCE']:
            temp_result = preprocessor(resource_id=resource_id)
            if temp_result is not None:
                resource_id = temp_result
        resource = get_by(self.session, self.model, resource_id,
                          self.primary_key)
        if resource is None:
            detail = 'No resource with ID {0}'.format(resource_id)
            return error_response(404, detail=detail)
        return self._get_resource_helper(resource)

    def _get_collection(self):
        try:
            filters, sort, group_by, single = self._collection_parameters()
        except (TypeError, ValueError, OverflowError) as exception:
            detail = 'Unable to decode filter objects as JSON list'
            return error_response(400, cause=exception, detail=detail)
        except SingleKeyError as exception:
            detail = 'Invalid format for filter[single] query parameter'
            return error_response(400, cause=exception, detail=detail)

        for preprocessor in self.preprocessors['GET_COLLECTION']:
            preprocessor(filters=filters, sort=sort, group_by=group_by,
                         single=single)

        return self._get_collection_helper(filters=filters, sort=sort,
                                           group_by=group_by, single=single)

    def get(self, resource_id, relation_name, related_resource_id):
        if resource_id is None:
            return self._get_collection()
        if relation_name is None:
            return self._get_resource(resource_id)
        if related_resource_id is None:
            return self._get_relation(resource_id, relation_name)
        return self._get_related_resource(resource_id, relation_name,
                                          related_resource_id)

    def delete(self, resource_id):
        for preprocessor in self.preprocessors['DELETE_RESOURCE']:
            temp_result = preprocessor(resource_id=resource_id)
            if temp_result is not None:
                resource_id = temp_result
        was_deleted = False
        instance = get_by(self.session, self.model, resource_id,
                          self.primary_key)
        if instance is None:
            detail = 'No resource found with ID {0}'.format(resource_id)
            return error_response(404, detail=detail)
        self.session.delete(instance)
        was_deleted = len(self.session.deleted) > 0
        self.session.commit()
        for postprocessor in self.postprocessors['DELETE_RESOURCE']:
            postprocessor(was_deleted=was_deleted)
        if not was_deleted:
            detail = 'There was no instance to delete.'
            return error_response(404, detail=detail)
        return {}, 204

    def post(self):
        try:
            data = json.loads(request.get_data()) or {}
        except (BadRequest, TypeError, ValueError, OverflowError) as exception:
            detail = 'Unable to decode data'
            return error_response(400, cause=exception, detail=detail)
        for preprocessor in self.preprocessors['POST_RESOURCE']:
            preprocessor(data=data)
        try:
            instance = self.deserialize(data)
            self.session.add(instance)
            self.session.commit()
        except ClientGeneratedIDNotAllowed as exception:
            detail = exception.message()
            return error_response(403, cause=exception, detail=detail)
        except ConflictingType as exception:
            detail = exception.message()
            return error_response(409, cause=exception, detail=detail)
        except DeserializationException as exception:
            detail = exception.message()
            return error_response(400, cause=exception, detail=detail)
        except self.validation_exceptions as exception:
            return self._handle_validation_exception(exception)
        fields_for_this = self.sparse_fields.get(self.collection_name)
        try:
            data = self.serialize(instance, only=fields_for_this)
        except SerializationException as exception:
            detail = 'Failed to serialize object'
            return error_response(400, cause=exception, detail=detail)
        primary_key = primary_key_value(instance, as_string=True)
        url = '{0}/{1}'.format(request.base_url, primary_key)
        headers = dict(Location=url)
        result = {'jsonapi': {'version': JSONAPI_VERSION}, 'data': data}
        try:
            included = self.get_all_inclusions(instance)
        except MultipleExceptions as e:
            return errors_from_serialization_exceptions(e.exceptions,
                                                        included=True)
        if included:
            result['included'] = included
        status = 201
        for postprocessor in self.postprocessors['POST_RESOURCE']:
            postprocessor(result=result)
        return result, status, headers

    def _update_instance(self, instance, data, resource_id):
        links = data.pop('relationships', {})
        for linkname, link in links.items():
            if not isinstance(link, dict):
                detail = ('missing relationship object for "{0}" in resource'
                          ' of type "{1}" with ID "{2}"')
                detail = detail.format(linkname, self.collection_name,
                                       resource_id)
                return error_response(400, detail=detail)
            if 'data' not in link:
                detail = 'relationship "{0}" is missing resource linkage'
                detail = detail.format(linkname)
                return error_response(400, detail=detail)
            linkage = link['data']
            related_model = get_related_model(self.model, linkname)
            if is_like_list(instance, linkname):
                if not self.allow_to_many_replacement:
                    detail = 'Not allowed to replace a to-many relationship'
                    return error_response(403, detail=detail)
                if not isinstance(linkage, list):
                    detail = ('"data" element for the to-many relationship'
                              ' "{0}" on the instance of "{1}" with ID "{2}"'
                              ' must be a list; maybe you intended to provide'
                              ' an empty list?')
                    detail = detail.format(linkname, self.collection_name,
                                           resource_id)
                    return error_response(400, detail=detail)
                newvalue = []
                not_found = []
                for rel in linkage:
                    expected_type = collection_name(related_model)
                    type_ = rel['type']
                    if type_ != expected_type:
                        detail = 'Type must be {0}, not {1}'
                        detail = detail.format(expected_type, type_)
                        return error_response(409, detail=detail)
                    id_ = rel['id']
                    inst = get_by(self.session, related_model, id_)
                    if inst is None:
                        not_found.append((id_, type_))
                    else:
                        newvalue.append(inst)
                if not_found:
                    detail = 'No object of type {0} found with ID {1}'
                    errors = [error(detail=detail.format(t, i))
                              for t, i in not_found]
                    return errors_response(404, errors)
            else:
                if linkage is None:
                    newvalue = None
                else:
                    expected_type = collection_name(related_model)
                    type_ = linkage['type']
                    if type_ != expected_type:
                        detail = 'Type must be {0}, not {1}'
                        detail = detail.format(expected_type, type_)
                        return error_response(409, detail=detail)
                    id_ = linkage['id']
                    inst = get_by(self.session, related_model, id_)
                    if inst is None:
                        detail = 'No object of type {0} found with ID {1}'
                        detail = detail.format(type_, id_)
                        return error_response(404, detail=detail)
                    newvalue = inst
            try:
                setattr(instance, linkname, newvalue)
            except self.validation_exceptions as exception:
                return self._handle_validation_exception(exception)

        data = data.pop('attributes', {})
        for field in data:
            if not has_field(self.model, field):
                detail = "Model does not have field '{0}'".format(field)
                return error_response(400, detail=detail)
        data = strings_to_datetimes(self.model, data)
        try:
            if data:
                for field, value in data.items():
                    setattr(instance, field, value)
            self.session.commit()
        except self.validation_exceptions as exception:
            return self._handle_validation_exception(exception)

    def patch(self, resource_id):
        try:
            data = json.loads(request.get_data()) or {}
        except (BadRequest, TypeError, ValueError, OverflowError) as exception:
            detail = 'Unable to decode data'
            return error_response(400, cause=exception, detail=detail)
        for preprocessor in self.preprocessors['PATCH_RESOURCE']:
            temp_result = preprocessor(resource_id=resource_id, data=data)
            if temp_result is not None:
                resource_id = temp_result
        instance = get_by(self.session, self.model, resource_id,
                          self.primary_key)
        if instance is None:
            detail = 'No instance with ID {0} in model {1}'.format(resource_id,
                                                                   self.model)
            return error_response(404, detail=detail)
        data = data.pop('data', {})
        if 'type' not in data:
            message = 'Must specify correct data type'
            return error_response(400, detail=message)
        if 'id' not in data:
            message = 'Must specify resource ID'
            return error_response(400, detail=message)
        type_ = data.pop('type')
        id_ = data.pop('id')
        if type_ != self.collection_name:
            message = ('Type must be {0}, not'
                       ' {1}').format(self.collection_name, type_)
            return error_response(409, detail=message)
        if id_ != resource_id:
            message = 'ID must be {0}, not {1}'.format(resource_id, id_)
            return error_response(409, detail=message)
        result = self._update_instance(instance, data, resource_id)
        if result is not None:
            return result
        if self.changes_on_update:
            result = dict(data=self.serialize(instance))
            status = 200
        else:
            result = dict()
            status = 204
        for postprocessor in self.postprocessors['PATCH_RESOURCE']:
            postprocessor(result=result)
        return result, status
