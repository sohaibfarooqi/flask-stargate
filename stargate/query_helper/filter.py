import inspect
from ..exception import UnknownField, ComparisonToNull
from sqlalchemy import Date, DateTime, Interval, Time, and_, or_
from dateutil.parser import parse as parse_datetime
import datetime
from sqlalchemy.sql.expression import ColumnElement
from sqlalchemy.orm import RelationshipProperty as RelProperty
from sqlalchemy.ext.associationproxy import AssociationProxy
from sqlalchemy.orm.attributes import InstrumentedAttribute
from ..utils import string_to_datetime

def get_related_association_proxy_model(attr):
    prop = attr.remote_attr.property
    for attribute in ('mapper', 'parent'):
        if hasattr(prop, attribute):
            return getattr(prop, attribute).class_
    return None

def _sub_operator(model, argument, fieldname):
    print(argument, fieldname)
    if isinstance(model, InstrumentedAttribute):
        submodel = model.property
    elif isinstance(model, AssociationProxy):
        submodel = get_related_association_proxy_model(model)
    fieldname = argument['name']
    operator = argument['op']
    argument = argument.get('val')
    return create_operation(submodel, fieldname, operator, argument)


OPERATORS = {
    # Operators which accept a single argument.
    'is_null': lambda f: f == None,
    'is_not_null': lambda f: f != None,
    # 'desc': lambda f: f.desc,
    # 'asc': lambda f: f.asc,
    # Operators which accept two arguments.
    '==': lambda f, a: f == a,
    'eq': lambda f, a: f == a,
    'equals': lambda f, a: f == a,
    'equal_to': lambda f, a: f == a,
    '!=': lambda f, a: f != a,
    'ne': lambda f, a: f != a,
    'neq': lambda f, a: f != a,
    'not_equal_to': lambda f, a: f != a,
    'does_not_equal': lambda f, a: f != a,
    '>': lambda f, a: f > a,
    'gt': lambda f, a: f > a,
    '<': lambda f, a: f < a,
    'lt': lambda f, a: f < a,
    '>=': lambda f, a: f >= a,
    'ge': lambda f, a: f >= a,
    'gte': lambda f, a: f >= a,
    'geq': lambda f, a: f >= a,
    '<=': lambda f, a: f <= a,
    'le': lambda f, a: f <= a,
    'lte': lambda f, a: f <= a,
    'leq': lambda f, a: f <= a,
    '<<': lambda f, a: f.op('<<')(a),
    '<<=': lambda f, a: f.op('<<=')(a),
    '>>': lambda f, a: f.op('>>')(a),
    '>>=': lambda f, a: f.op('>>=')(a),
    '<>': lambda f, a: f.op('<>')(a),
    '&&': lambda f, a: f.op('&&')(a),
    'ilike': lambda f, a: f.ilike(a),
    'like': lambda f, a: f.like(a),
    'not_like': lambda f, a: ~f.like(a),
    'in': lambda f, a: f.in_(a),
    'not_in': lambda f, a: ~f.in_(a),
    # Operators which accept three arguments.
    'has': lambda f, a, fn: f.has(_sub_operator(f, a, fn)),
    'any': lambda f, a, fn: f.any(_sub_operator(f, a, fn)),
}


class Filter:

    def __init__(self, fieldname, operator, argument=None, otherfield=None):
        self.fieldname = fieldname
        self.operator = operator
        self.argument = argument
        self.otherfield = otherfield

    @staticmethod
    def from_dictionary(model, dictionary):
        if 'or' not in dictionary and 'and' not in dictionary:
            fieldname = dictionary.get('name')
            if not hasattr(model, fieldname):
                raise UnknownField("No Field found {0}",format(fieldname))
            operator = dictionary.get('op')
            otherfield = dictionary.get('field')
            argument = dictionary.get('val')
            argument = string_to_datetime(model, fieldname, argument)
            return Filter(fieldname, operator, argument, otherfield)
        
        from_dict = Filter.from_dictionary
        
        if 'or' in dictionary:
            subfilters = dictionary.get('or')
            return DisjunctionFilter(*[from_dict(model, filter_)
                                       for filter_ in subfilters])
        else:
            subfilters = dictionary.get('and')
            return ConjunctionFilter(*[from_dict(model, filter_)
                                       for filter_ in subfilters])


class JunctionFilter(Filter):
    
    def __init__(self, *subfilters):
        self.subfilters = subfilters

    def __iter__(self):
        return iter(self.subfilters)


class ConjunctionFilter(JunctionFilter):
    pass

class DisjunctionFilter(JunctionFilter):
    pass

def create_operation(model, fieldname, operator, argument):
    
    opfunc = OPERATORS[operator]
    numargs = len(inspect.signature(opfunc).parameters)
    field = getattr(model, fieldname)
    if numargs == 1:
        return opfunc(field)
    if argument is None:
        msg = ('To compare a value to NULL, use the is_null/is_not_null '
               'operators.')
        raise ComparisonToNull(msg)
    if numargs == 2:
        return opfunc(field, argument)
    return opfunc(field, argument, fieldname)


def create_filter(model, filt):
    if not isinstance(filt, JunctionFilter):
        fname = filt.fieldname
        val = filt.argument
        if filt.otherfield:
            val = getattr(model, filt.otherfield)
        return create_operation(model, fname, filt.operator, val)
    if isinstance(filt, ConjunctionFilter):
        return and_(create_filter(model, f) for f in filt)
    return or_(create_filter(model, f) for f in filt)
