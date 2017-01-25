from flask import jsonify, current_app
from werkzeug.exceptions import Conflict, BadRequest, NotFound, InternalServerError, UnsupportedMediaType, UnprocessableEntity
from werkzeug.http import HTTP_STATUS_CODES

"""Werkzeug Exceptions"""
class StargateException(Exception):
    werkzeug_exception = InternalServerError

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

class SingleKeyError(ValidationException):
    super(SingleKeyError, self).__init__()
    self.msg = msg

class ProcessingException(HTTPException):

    def __init__(self, id_=None, links=None, status=400, code=None, title=None,
                 detail=None, source=None, meta=None, *args, **kw):
        super(ProcessingException, self).__init__(*args, **kw)
        self.id_ = id_
        self.links = links
        self.status = status
        self.code_ = code
        self.code = status
        self.title = title
        self.detail = detail
        self.source = source
        self.meta = meta

class SerializationException(ProcessingException):
    def __init__(self, instance, message=None, resource=None, *args, **kw):
        super(SerializationException, self).__init__(*args, **kw)
        self.resource = resource
        self.message = message
        self.instance = instance

class PaginationError(ValidationException):
    super(PaginationError, self).__init__()
    self.msg = msg

class DeserializationException(ProcessingException):
    
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
