import inspect

from sqlalchemy import and_
from sqlalchemy import or_
from sqlalchemy.ext.associationproxy import AssociationProxy
from sqlalchemy.orm import aliased
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql import false as FALSE

from .helpers import get_model
from .helpers import get_related_model
from .helpers import get_related_association_proxy_model
from .helpers import primary_key_names
from .helpers import primary_key_value
from .helpers import session_query
from .helpers import string_to_datetime


class ComparisonToNull(Exception):
    pass


class UnknownField(Exception):

    def __init__(self, field):

        self.field = field


def _sub_operator(model, argument, fieldname):
    if isinstance(model, InstrumentedAttribute):
        submodel = model.property.mapper.class_
    elif isinstance(model, AssociationProxy):
        submodel = get_related_association_proxy_model(model)
    else:
        # TODO what to do here?
        pass
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


class Filter(object):

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
                raise UnknownField(fieldname)
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

class DisjunctionFilter(JunctionFilter):

def create_operation(model, fieldname, operator, argument):
    opfunc = OPERATORS[operator]
    numargs = len(inspect.getargspec(opfunc).args)
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


def search_relationship(session, instance, relation, filters=None, sort=None,
                        group_by=None):
    model = get_model(instance)
    related_model = get_related_model(model, relation)
    query = session_query(session, related_model)

    relationship = getattr(instance, relation)
    primary_keys = set(primary_key_value(inst) for inst in relationship)
    if not primary_keys:
        return query.filter(FALSE())
    query = query.filter(primary_key_value(related_model).in_(primary_keys))

    return search(session, related_model, filters=filters, sort=sort,
                  group_by=group_by, _initial_query=query)


def search(session, model, filters=None, sort=None, group_by=None,
           _initial_query=None):
    if _initial_query is not None:
        query = _initial_query
    else:
        query = session_query(session, model)

    filters = [Filter.from_dictionary(model, f) for f in filters]
    filters = [create_filter(model, f) for f in filters]
    query = query.filter(*filters)

    if sort:
        for (symbol, field_name) in sort:
            direction_name = 'asc' if symbol == '+' else 'desc'
            if '.' in field_name:
                field_name, field_name_in_relation = field_name.split('.')
                relation_model = aliased(get_related_model(model, field_name))
                field = getattr(relation_model, field_name_in_relation)
                direction = getattr(field, direction_name)
                query = query.join(relation_model)
                query = query.order_by(direction())
            else:
                field = getattr(model, field_name)
                direction = getattr(field, direction_name)
                query = query.order_by(direction())
    else:
        pks = primary_key_names(model)
        pk_order = (getattr(model, field).asc() for field in pks)
        query = query.order_by(*pk_order)

    # Group the query.
    if group_by:
        for field_name in group_by:
            if '.' in field_name:
                field_name, field_name_in_relation = field_name.split('.')
                relation_model = get_related_model(model, field_name)
                field = getattr(relation_model, field_name_in_relation)
                query = query.join(relation_model)
                query = query.group_by(field)
            else:
                field = getattr(model, field_name)
                query = query.group_by(field)

    return query
