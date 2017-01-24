
"""Module: RequestManager
Declared Exceptions: IllegalArgumentError,
	
	IllegalArgumentError:
		Args: str(msg) => detail message
		Thrown: When argument passed to RequestManger do not conform to type accepted by either meth:__init__ or meth:regiter_resource_as_api"""
class IllegalArgumentError(Exception):
    pass
#######################################################################################################################################################

"""Module: All View Function(CollectionAPI,)
Declared Exceptions: ComparisonToNull,UnknownField,SingleKeyError,ProcessingException,
	
	ComparisonToNull:
		Args: str(msg) => detail message
		Thrown: When argument passed to RequestManger do not conform to type accepted by either meth:__init__ or meth:regiter_resource_as_api
	
	UnknownField:
		Args: str(msg) => detail message
		Thrown: When argument passed to RequestManger do not conform to type accepted by either meth:__init__ or meth:regiter_resource_as_api
	
	SingleKeyError:
		Args: str(msg) => detail message
		Thrown: When argument passed to RequestManger do not conform to type accepted by either meth:__init__ or meth:regiter_resource_as_api
	
	ProcessingException:
		Args: str(msg) => detail message
		Thrown: When argument passed to RequestManger do not conform to type accepted by either meth:__init__ or meth:regiter_resource_as_api"""
class ComparisonToNull(Exception):
    pass

class UnknownField(Exception):

    def __init__(self, field):
        self.field = field

class SingleKeyError(KeyError):
    pass

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
#######################################################################################################################################################

"""Module: Serializer
Declared Exceptions: SerializationException,
	
	SerializationException:
		Args: str(msg) => detail message
		Thrown: When argument passed to RequestManger do not conform to type accepted by either meth:__init__ or meth:regiter_resource_as_api"""
class SerializationException(Exception):
    def __init__(self, instance, message=None, resource=None, *args, **kw):
        super(SerializationException, self).__init__(*args, **kw)
        self.resource = resource
        self.message = message
        self.instance = instance
#######################################################################################################################################################

"""Module: Pagination
Declared Exceptions: PaginationError,
	
	PaginationError:
		Args: str(msg) => detail message
		Thrown: When argument passed to RequestManger do not conform to type accepted by either meth:__init__ or meth:regiter_resource_as_api"""
"""Pagination Errors"""
class PaginationError(Exception):
    pass
#######################################################################################################################################################

"""Module: All View Function(CollectionAPI,)
Declared Exceptions: ComparisonToNull,UnknownField,SingleKeyError,ProcessingException,
	
	DeserializationException:
		Args: str(msg) => detail message
		Thrown: When argument passed to RequestManger do not conform to type accepted by either meth:__init__ or meth:regiter_resource_as_api
	ClientGeneratedIDNotAllowed:
		Args: str(msg) => detail message
		Thrown: When argument passed to RequestManger do not conform to type accepted by either meth:__init__ or meth:regiter_resource_as_api
	MissingInformation:
		Args: str(msg) => detail message
		Thrown: When argument passed to RequestManger do not conform to type accepted by either meth:__init__ or meth:regiter_resource_as_api
	MissingData:
		Args: str(msg) => detail message
		Thrown: When argument passed to RequestManger do not conform to type accepted by either meth:__init__ or meth:regiter_resource_as_api
	MissingID:
		Args: str(msg) => detail message
		Thrown: When argument passed to RequestManger do not conform to type accepted by either meth:__init__ or meth:regiter_resource_as_api
	MissingType:
		Args: str(msg) => detail message
		Thrown: When argument passed to RequestManger do not conform to type accepted by either meth:__init__ or meth:regiter_resource_as_api
	ConflictingType:
		Args: str(msg) => detail message
		Thrown: When argument passed to RequestManger do not conform to type accepted by either meth:__init__ or meth:regiter_resource_as_api"""
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

#######################################################################################################################################################