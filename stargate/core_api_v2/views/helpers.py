from sqlalchemy.exc import OperationalError
from sqlalchemy.inspection import inspect as sqlalchemy_inspect
from sqlalchemy.sql import func


def upper_keys(dictionary):
    return dict((k.upper(), v) for k, v in dictionary.items())


def evaluate_functions(session, model, functions):
   
    if not model or not functions:
        return []
    processed = []
    for function in functions:
        if 'name' not in function:
            raise KeyError('Missing `name` key in function object')
        if 'field' not in function:
            raise KeyError('Missing `field` key in function object')
        funcname, fieldname = function['name'], function['field']
       
        funcobj = getattr(func, funcname)
        try:
            field = getattr(model, fieldname)
        except AttributeError as exception:
            exception.field = fieldname
            raise exception
        
        processed.append(funcobj(field))
    
    try:
        evaluated = session.query(*processed).one()
    except OperationalError as exception:
       
        original_error_msg = exception.args[0]
        bad_function = original_error_msg[37:]
        exception.function = bad_function
        raise exception
    return list(evaluated)


def count(session, query):
   counts = query.selectable.with_only_columns([func.count()])
    num_results = session.execute(counts.order_by(None)).scalar()
    if num_results is None or query._limit is not None:
        return query.order_by(None).count()
    return num_results


def changes_on_update(model):
    return any(column.onupdate is not None
               for column in sqlalchemy_inspect(model).columns)
