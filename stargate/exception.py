from flask import jsonify, current_app
from werkzeug.exceptions import NotAcceptable, Conflict, BadRequest, NotFound, InternalServerError, UnsupportedMediaType, UnprocessableEntity
from werkzeug.http import HTTP_STATUS_CODES

"""Werkzeug Exceptions"""
class StargateException(Exception):
    werkzeug_exception = InternalServerError

    def __init__(self, msg=None):
        self.msg = msg
    
    @property
    def status_code(self):
        return self.werkzeug_exception.code

    def as_dict(self):
        return {
            'status': self.status_code,
            'message': self.msg if self.msg else HTTP_STATUS_CODES.get(self.status_code, '')
        }

    def get_response(self):
        response = jsonify(self.as_dict())
        response.status_code = self.status_code
        return response

class ResourceNotFound(StargateException):
    werkzeug_exception = NotFound

    def __init__(self, resource, msg = None, id = None):
        super(ResourceNotFound, self).__init__()
        self.resource = resource
        self.msg = msg
        self.id = id

    def as_dict(self):
        dct = super(ResourceNotFound, self).as_dict()
        dct['resource'] = self.resource
        dct['primary_key'] = self.id
        return dct   

class MediaTypeNotSupported(StargateException):
    werkzeug_exception = UnsupportedMediaType

class ValidationException(StargateException):
    werkzeug_exception = BadRequest

class ConflictException(StargateException):
    werkzeug_exception = Conflict
    
    def __init__(self, msg, **kwargs):
        super(IllegalArgumentError, self).__init__()
        self.msg = msg
class NotAcceptable(StargateException):
    werkzeug_exception = NotAcceptable

class ProcessingException(StargateException):
    werkzeug_exception = UnprocessableEntity

"""Application Custom Exceptions"""
class IllegalArgumentError(ValidationException):
    
    def __init__(self, msg, **kwargs):
        super(IllegalArgumentError, self).__init__()
        self.msg = msg

class ComparisonToNull(ValidationException):
    def __init__(self, msg, **kwargs):
        super(ComparisonToNull, self).__init__()
        self.msg = msg

class UnknownField(ValidationException):

    def __init__(self, field, resource):
        super(UnknownField, self).__init__()
        self.field = field
        self.msg = "Unknown field {0} in model {1}".format(field, resource)

    
    def as_dict(self):
        dct = super(UnknownField, self).as_dict()
        dct['field'] = self.field
        return dct

class SingleKeyError(ValidationException):
    def __init__(self, msg, **kwargs):
        super(SingleKeyError, self).__init__()
        self.msg = msg

class SerializationException(ProcessingException):
    
    def __init__(self, instance, message=None, *args, **kw):
        super(SerializationException, self).__init__(*args, **kw)
        self.instance = instance

    def as_dict(self):
        dct = super(SerializationException, self).as_dict()
        dct['instance'] = self.instance
        return dct

class PaginationError(ValidationException):
    def __init__(self, msg, **kwargs):
        super(PaginationError, self).__init__()
        self.msg = msg

class DeserializationException(ProcessingException):
    
    def __init__(self, *args, **kw):
        super(DeserializationException, self).__init__(*args, **kw)
        self.msg = kw['msg'] if kw['msg'] else 'Failed to deserialize object'

class ClientGeneratedIDNotAllowed(DeserializationException):
    def __init__(self, msg, **kwargs):
        super(ClientGeneratedIDNotAllowed, self).__init__()
        self.msg = msg

class MissingdataException (DeserializationException):
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

    def as_dict(self):
        dct = super(UnknownField, self).as_dict()
        dct['relation_name'] = self.relation_name
        dct['details'] = self.details
        return dct

class MissingData(MissingdataException):
    element = 'data'


class MissingID(MissingdataException):
    element = 'id'


class MissingType(MissingdataException):
    element = 'type'