"""Application exceptions. Base Exception class for this app is `StargateException`. 
All application exceptions are caught here and send back to client in a prescribed format. 
Exceptions are further grouped so that we can located the part of code causing a specific 
exception. Werkzeug exceptions are also mapped here.

"""

from flask import jsonify
from werkzeug.exceptions import NotAcceptable, Conflict, BadRequest, NotFound, InternalServerError, UnsupportedMediaType, UnprocessableEntity
from werkzeug.http import HTTP_STATUS_CODES

############################--MAIN APPLICATION ERROR CLASS--##################################
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
            'message': self.msg if self.msg else HTTP_STATUS_CODES.get(self.status_code, ''),
            'details': {'_exception_class': self.__name__}
        }

    def get_response(self):
        response = jsonify(self.as_dict())
        response.status_code = self.status_code
        return response
############################--NOT-FOUND ERRORS--############################################
class ResourceNotFound(StargateException):
    werkzeug_exception = NotFound

    def __init__(self, resource, id = None, msg = None):
        super(ResourceNotFound, self).__init__()
        self.resource = resource
        self.msg = msg
        self.id = id

    def as_dict(self):
        dct = super(ResourceNotFound, self).as_dict()
        dct['details'].update({'resource' : self.resource, 'primary_key' : self.id})
        return dct   
############################--CONFLICT ERRORS--############################################
class ConflictException(StargateException):
    werkzeug_exception = Conflict
    
    def __init__(self, msg, **kwargs):
        super(ConflictException, self).__init__()
        self.msg = msg
############################--MEDIATYPE ERRORS--############################################
class MediaTypeNotSupported(StargateException):
    werkzeug_exception = UnsupportedMediaType

class NotAcceptable(StargateException):
    werkzeug_exception = NotAcceptable

############################--VALIDATION ERRORS--############################################
class ValidationError(StargateException):
    werkzeug_exception = BadRequest

    def __init__(self, msg, **kwargs):
        super(ValidationError, self).__init__()
        self.msg = msg

class ComparisonToNull(ValidationError):
    def __init__(self, msg, **kwargs):
        super(ComparisonToNull, self).__init__()
        self.msg = msg

class UnknownField(ValidationError):
    def __init__(self, field, resource):
        super(UnknownField, self).__init__()
        self.field = field
        self.resource = resource
        self.msg = "Unknown field {0} in model {1}".format(field, resource)
    
    def as_dict(self):
        dct = super(UnknownField, self).as_dict()
        dct['details'].update({'field' : self.field, 'resource': self.resource})
        return dct

class UnknownRelation(ValidationError):
    def __init__(self, relation, resource):
        super(UnknownRelation, self).__init__()
        self.relation = relation
        self.resource = resource
        self.msg = "Unknown relation {0} in model {1}".format(field, resource)
    
    def as_dict(self):
        dct = super(UnknownRelation, self).as_dict()
        dct['details'].update({'relation' : self.relation,  'resource': self.resource})
        return dct

class IllegalArgumentError(ValidationError):
    
    def __init__(self, msg, **kwargs):
        super(IllegalArgumentError, self).__init__()
        self.msg = msg

############################--PROCESSING ERRORS--############################################
class ProcessingException(StargateException):
    werkzeug_exception = UnprocessableEntity       

class MissingData(ProcessingException):
    def __init__(self, model, *args, **kw):
        super(MissingData, self).__init__(*args, **kw)
        self.msg  = "Missing `data` key for model {0}".format(model)

class MissingPrimaryKey(ProcessingException):
    def __init__(self, model, *args, **kw):
        super(MissingPrimaryKey, self).__init__(*args, **kw)
        self.msg  = "Missing `id` key for model {0}".format(model)

class DatabaseError(ProcessingException):
    def __init__(self, msg, *args, **kw):
        super(DatabaseError, self).__init__(*args, **kw)
        self.msg  = "Error occured in db transction {0}".format(model)

class SerializationException(ProcessingException):
    
    def __init__(self, instance, message=None, *args, **kw):
        super(SerializationException, self).__init__(*args, **kw)
        self.instance = instance
        DEFAULT_MSG = "Failed to Deserialize Object"
        self.msg  = message if message is not None else DEFAULT_MSG
    
    def as_dict(self):
        dct = super(SerializationException, self).as_dict()
        dct['details'].update({'instance' : self.instance})
        return dct

class DeserializationException(ProcessingException):
    
    def __init__(self, instance, message = None, *args, **kw):
        super(DeserializationException, self).__init__(*args, **kw)
        DEFAULT_MSG = "Failed to Deserialize Object"
        self.msg = message if message is not None else DEFAULT_MSG

    def as_dict(self):
        dct = super(SerializationException, self).as_dict()
        dct['details'].update({'instance' : self.instance})
        return dct
###############################################################################################