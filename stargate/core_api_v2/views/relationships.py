from flask import json
from flask import request
from werkzeug.exceptions import BadRequest

from ..helpers import collection_name
from ..helpers import get_by
from ..helpers import get_related_model
from ..helpers import is_like_list
from .base import APIBase
from .base import error
from .base import error_response
from .base import errors_response
from .base import SingleKeyError


class RelationshipAPI(APIBase):
   
    def __init__(self, session, model,
                 allow_delete_from_to_many_relationships=False, *args, **kw):
        super(RelationshipAPI, self).__init__(session, model, *args, **kw)
        self.allow_delete_from_to_many_relationships = \
            allow_delete_from_to_many_relationships

    def collection_processor_type(self, *args, **kw):
        return 'TO_MANY_RELATIONSHIP'

    def resource_processor_type(self, *args, **kw):
        return 'TO_ONE_RELATIONSHIP'

    def use_resource_identifiers(self):
        return True

    def get(self, resource_id, relation_name):
       
        for preprocessor in self.preprocessors['GET_RELATIONSHIP']:
            temp_result = preprocessor(resource_id=resource_id,
                                       relation_name=relation_name)
            
            if temp_result is not None:
                resource_id = temp_result
        primary_resource = get_by(self.session, self.model, resource_id,
                                  self.primary_key)
        if primary_resource is None:
            detail = 'No resource with ID {0}'.format(resource_id)
            return error_response(404, detail=detail)
        if is_like_list(primary_resource, relation_name):
            try:
                filters, sort, group_by, single = self._collection_parameters()
            except (TypeError, ValueError, OverflowError) as exception:
                detail = 'Unable to decode filter objects as JSON list'
                return error_response(400, cause=exception, detail=detail)
            except SingleKeyError as exception:
                detail = 'Invalid format for filter[single] query parameter'
                return error_response(400, cause=exception, detail=detail)
            return self._get_collection_helper(resource=primary_resource,
                                               relation_name=relation_name,
                                               filters=filters, sort=sort,
                                               group_by=group_by,
                                               single=single)
        resource = getattr(primary_resource, relation_name)
        return self._get_resource_helper(resource,
                                         primary_resource=primary_resource,
                                         relation_name=relation_name)

    def post(self, resource_id, relation_name):
      
        try:
            data = json.loads(request.get_data()) or {}
        except (BadRequest, TypeError, ValueError, OverflowError) as exception:
            detail = 'Unable to decode data'
            return error_response(400, cause=exception, detail=detail)
        for preprocessor in self.preprocessors['POST_RELATIONSHIP']:
            temp_result = preprocessor(resource_id=resource_id,
                                       relation_name=relation_name, data=data)
            if temp_result is not None:
                resource_id, relation_name = temp_result
        instance = get_by(self.session, self.model, resource_id,
                          self.primary_key)
     
        if instance is None:
            detail = 'No instance with ID {0} in model {1}'
            detail = detail.format(resource_id, self.model)
            return error_response(404, detail=detail)
       
        if not hasattr(instance, relation_name):
            detail = 'Model {0} has no relation named {1}'
            detail = detail.format(self.model, relation_name)
            return error_response(404, detail=detail)
        related_model = get_related_model(self.model, relation_name)
        related_value = getattr(instance, relation_name)
       
        data = data.pop('data', {})
        for rel in data:
            if 'type' not in rel:
                detail = 'Must specify correct data type'
                return error_response(400, detail=detail)
            if 'id' not in rel:
                detail = 'Must specify resource ID'
                return error_response(400, detail=detail)
            type_ = rel['type']
          
            if type_ != collection_name(related_model):
                detail = ('Type must be {0}, not'
                          ' {1}').format(collection_name(related_model), type_)
                return error_response(409, detail=detail)
            new_value = get_by(self.session, related_model, rel['id'])
            if new_value is None:
                detail = ('No object of type {0} found with ID'
                          ' {1}').format(type_, rel['id'])
                return error_response(404, detail=detail)
           
            if new_value not in related_value:
                try:
                    related_value.append(new_value)
                except self.validation_exceptions as exception:
                    return self._handle_validation_exception(exception)
        
        for postprocessor in self.postprocessors['POST_RELATIONSHIP']:
            postprocessor()
        return {}, 204

    def patch(self, resource_id, relation_name):
      
        try:
            data = json.loads(request.get_data()) or {}
        except (BadRequest, TypeError, ValueError, OverflowError) as exception:
            detail = 'Unable to decode data'
            return error_response(400, cause=exception, detail=detail)
        for preprocessor in self.preprocessors['PATCH_RELATIONSHIP']:
            temp_result = preprocessor(instance_id=resource_id,
                                       relation_name=relation_name, data=data)
           
            if temp_result is not None:
                resource_id, relation_name = temp_result
        instance = get_by(self.session, self.model, resource_id,
                          self.primary_key)
       
        if instance is None:
            detail = 'No instance with ID {0} in model {1}'
            detail = detail.format(resource_id, self.model)
            return error_response(404, detail=detail)
       
        if not hasattr(instance, relation_name):
            detail = 'Model {0} has no relation named {1}'
            detail = detail.format(self.model, relation_name)
            return error_response(404, detail=detail)
        related_model = get_related_model(self.model, relation_name)
      
        data = data.pop('data', {})
       
        if data is None:
            if is_like_list(instance, relation_name):
                detail = 'Cannot set null value on a to-many relationship'
                return error_response(400, detail=detail)
            setattr(instance, relation_name, None)
        else:
            
            if isinstance(data, list):
               
                if not self.allow_to_many_replacement:
                    detail = 'Not allowed to replace a to-many relationship'
                    return error_response(403, detail=detail)
                replacement = []
                for rel in data:
                    if 'type' not in rel:
                        detail = 'Must specify correct data type'
                        return error_response(400, detail=detail)
                    if 'id' not in rel:
                        detail = 'Must specify resource ID or IDs'
                        return error_response(400, detail=detail)
                    type_ = rel['type']
                   
                    if type_ != collection_name(related_model):
                        detail = 'Type must be {0}, not {1}'
                        detail = detail.format(collection_name(related_model),
                                               type_)
                        return error_response(409, detail=detail)
                    id_ = rel['id']
                    obj = get_by(self.session, related_model, id_)
                    replacement.append(obj)
           
            else:
                if 'type' not in data:
                    detail = 'Must specify correct data type'
                    return error_response(400, detail=detail)
                if 'id' not in data:
                    detail = 'Must specify resource ID or IDs'
                    return error_response(400, detail=detail)
                type_ = data['type']
               
                if type_ != collection_name(related_model):
                    detail = ('Type must be {0}, not'
                              ' {1}').format(collection_name(related_model),
                                             type_)
                    return error_response(409, detail=detail)
                id_ = data['id']
                replacement = get_by(self.session, related_model, id_)
           
            if replacement is None:
                detail = ('No object of type {0} found'
                          ' with ID {1}').format(type_, id_)
                return error_response(404, detail=detail)
            if (isinstance(replacement, list)
                and any(value is None for value in replacement)):
                not_found = (rel for rel, value in zip(data, replacement)
                             if value is None)
                detail = 'No object of type {0} found with ID {1}'
                errors = [error(detail=detail.format(rel['type'], rel['id']))
                          for rel in not_found]
                return errors_response(404, errors)
           
            try:
                setattr(instance, relation_name, replacement)
            except self.validation_exceptions as exception:
                return self._handle_validation_exception(exception)
        
        for postprocessor in self.postprocessors['PATCH_RELATIONSHIP']:
            postprocessor()
        return {}, 204

    def delete(self, resource_id, relation_name):
       
        if not self.allow_delete_from_to_many_relationships:
            detail = 'Not allowed to delete from a to-many relationship'
            return error_response(403, detail=detail)
       
        try:
            data = json.loads(request.get_data()) or {}
        except (BadRequest, TypeError, ValueError, OverflowError) as exception:
           
            detail = 'Unable to decode data'
            return error_response(400, cause=exception, detail=detail)
        was_deleted = False
        for preprocessor in self.preprocessors['DELETE_RELATIONSHIP']:
            temp_result = preprocessor(instance_id=resource_id,
                                       relation_name=relation_name)
           
            if temp_result is not None:
                resource_id = temp_result
        instance = get_by(self.session, self.model, resource_id,
                          self.primary_key)
        
        if not hasattr(instance, relation_name):
            detail = 'No such link: {0}'.format(relation_name)
            return error_response(404, detail=detail)
        
        related_model = get_related_model(self.model, relation_name)
        related_type = collection_name(related_model)
        relation = getattr(instance, relation_name)
        data = data.pop('data')
        not_found = []
        to_remove = []
        for rel in data:
            if 'type' not in rel:
                detail = 'Must specify correct data type'
                return error_response(400, detail=detail)
            if 'id' not in rel:
                detail = 'Must specify resource ID'
                return error_response(400, detail=detail)
            type_ = rel['type']
            id_ = rel['id']
            if type_ != related_type:
                detail = ('Conflicting type: expected {0} but got type {1} for'
                          ' linkage object with ID {2}')
                detail = detail.format(related_type, type_, id_)
                return error_response(409, detail=detail)
            resource = get_by(self.session, related_model, id_)
            if resource is None:
                not_found.append((type_, id_))
            else:
                to_remove.append(resource)
        if not_found:
            detail = 'No resource of type {0} and ID {1} found'
            errors = [error(detail=detail.format(t, i)) for t, i in not_found]
            return errors_response(404, errors)
       
        for resource in to_remove:
            try:
                relation.remove(resource)
            except ValueError:
               
                pass
        was_deleted = len(self.session.dirty) > 0
        self.session.commit()
        for postprocessor in self.postprocessors['DELETE_RELATIONSHIP']:
            postprocessor(was_deleted=was_deleted)
        if not was_deleted:
            detail = 'There was no instance to delete'
            return error_response(404, detail=detail)
        return {}, 204
