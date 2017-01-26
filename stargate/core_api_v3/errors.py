from .exception import ProcessingException, ValidationException, ConflictException
from functools import wraps

ERROR_FIELDS = ('id_', 'links', 'status', 'code_', 'title', 'detail', 'source',
                'meta')

CONFLICT_INDICATORS = ('conflicts with', 'UNIQUE constraint failed',
						'is not unique')

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
            raise ProcessingException(exception)
    return new_func

def catch_integrity_errors(session):
    def decorated(func):
        @wraps(func)
        def wrapped(*args, **kw):
            try:
                return func(*args, **kw)
            except SQLAlchemyError as exception:
                session.rollback()
                exception_string = str(exception)
                if any(s in exception_string for s in CONFLICT_INDICATORS):
                    raise ConflictException(exception_string)
                else:
                    raise ValidationException(exception_string)
            return wrapped
        return decorated
#####################################################################################################