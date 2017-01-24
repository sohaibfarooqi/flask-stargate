from .exception import is_conflict

ERROR_FIELDS = ('id_', 'links', 'status', 'code_', 'title', 'detail', 'source',
                'meta')

"""Utility function for class"""
def un_camel_case(s):
    return re.sub(r'(?<=\w)([A-Z])', r' \1', s)
#####################################################################################################

"""View Function Error handling Decorators"""
def catch_processing_exceptions(func):
    @wraps(func)
    def new_func(*args, **kw):
        try:
            return func(*args, **kw)
        except ProcessingException as exception:
            kw = dict((key, getattr(exception, key)) for key in ERROR_FIELDS)
            kw['code'] = kw.pop('code_')
            return error_response(cause = exception, **kw)
    return new_func

def catch_integrity_errors(session):
    
    def decorated(func):
        @wraps(func)
        def wrapped(*args, **kw):
            try:
                return func(*args, **kw)
            except SQLAlchemyError as exception:
                session.rollback()
                status = 409 if is_conflict(exception) else 400
                detail = str(exception)
                title = un_camel_case(exception.__class__.__name__)
                return error_response(status, cause=exception, detail=detail,
                                      title=title)
        return wrapped
    return decorated
#####################################################################################################

class Errors:
	def extract_error_messages(exception):
	    if isinstance(exception, DeserializationException):
	        return exception.args[0]
	    if hasattr(exception, 'errors'):
	        return exception.errors
	    if hasattr(exception, 'message'):
	        try:
	            left, right = str(exception).rsplit(':', 1)
	            left_bracket = left.rindex('[')
	            right_bracket = right.rindex(']')
	        except ValueError as exc:
	            current_app.logger.exception(str(exc))
	            return None
	        msg = right[:right_bracket].strip(' "')
	        fieldname = left[left_bracket + 1:].strip()
	        return {fieldname: msg}
	    return None

	def error(id_=None, links=None, status=None, code=None, title=None,
          detail=None, source=None, meta=None):
	    if all(kwvalue is None for kwvalue in locals().values()):
	        raise ValueError('At least one of the arguments must not be None.')
	    return {'id': id_, 'links': links, 'status': status, 'code': code,
	            'title': title, 'detail': detail, 'source': source, 'meta': meta}

	def error_response(status=400, cause=None, **kw):
	    if cause is not None:
	        current_app.logger.exception(str(cause))
	    kw['status'] = status
	    return errors_response(status, [error(**kw)])

	def errors_response(status, errors):
	    document = {'errors': errors, 'jsonapi': {'version': JSONAPI_VERSION},
	                'meta': {_STATUS: status}}
	    return document, status

	def error_from_serialization_exception(exception, included=False):
	    type_ = collection_name(get_model(exception.instance))
	    id_ = primary_key_value(exception.instance)
	    if exception.message is not None:
	        detail = exception.message
	    else:
	        resource = 'included resource' if included else 'resource'
	        detail = 'Failed to serialize {0} of type {1} and ID {2}'
	        detail = detail.format(resource, type_, id_)
	    return error(status=500, detail=detail)

	def errors_from_serialization_exceptions(exceptions, included=False):
	    _to_error = partial(error_from_serialization_exception, included=included)
	    errors = list(map(_to_error, exceptions))
	    return errors_response(500, errors)