"""Collection filteration utility. Convert dict() representation of filters to SQLAlcehmy filter(s). Supports Conjunction 
and Disjunction Filters. Also contains a list of supported `OPERATORS`(unary, binary, teritary).

"""

import inspect
from .exception import UnknownField, ComparisonToNull, UnknownOperator
from sqlalchemy import Date, DateTime, Interval, Time, and_, or_
from dateutil.parser import parse as parse_datetime
import datetime
from sqlalchemy.sql.expression import ColumnElement
from sqlalchemy.orm import RelationshipProperty as RelProperty
from sqlalchemy.ext.associationproxy import AssociationProxy
from sqlalchemy.orm.attributes import InstrumentedAttribute
from .utils import string_to_datetime, get_related_association_proxy_model

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
    # Operators which accept a List of values.
    'in': lambda f, a: f.in_(a),
    'not_in': lambda f, a: ~f.in_(a),
    # Operators which accept three arguments.
    'has': lambda f, a, fn: f.has(_sub_operator(f, a, fn)),
    'any': lambda f, a, fn: f.any(_sub_operator(f, a, fn)),
}


class Filter:
    """Convert JSON representation of filters to SQL Filter expression. It Recursively build filters
    in case of JunctionFilters are present in expression.

    :param fieldname: Resource field name.
    :param operator: SQL operator to be applied. 
    :param argument: Value to be comared with. 
    
    """
    def __init__(self, fieldname, operator, argument=None):
        self.fieldname = fieldname
        self.operator = operator
        self.argument = argument
        
    @staticmethod
    def from_json(model, filters):
        """This is public method of class. It recursively build filter expression if 
        `or` or `and` key word is present in filter json.
        
        :param filters: filter json representation

        Example filter expression:
        
            - [{"name":"age","op":"in","val":"10,11,12"}]
            - [{"name":"age","op":"is_not_null"}]
            - [{"name":"age","op":"eq","val":10}]

        """
        if 'or' not in filters and 'and' not in filters:
            fieldname = filters.get('name')
            if not hasattr(model, fieldname):
                raise UnknownField("No Field found {0}",format(fieldname))
            operator = filters.get('op')
            argument = filters.get('val')    
            argument = string_to_datetime(model, fieldname, argument)
            return Filter(fieldname, operator, argument)
        
        from_dict = Filter.from_json
        
        if 'or' in filters:
            subfilters = filters.get('or')
            return DisjunctionFilter(*[from_dict(model, filter_)
                                       for filter_ in subfilters])
        else:
            subfilters = filters.get('and')
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
    
    field = getattr(model, fieldname)
    
    if operator in OPERATORS:
        opfunc = OPERATORS[operator]
        numargs = len(inspect.signature(opfunc).parameters)
        
        #Unary Operators
        if numargs == 1:
            return opfunc(field)
        
        #Binary Operator Acception List of Values
        elif numargs == 2:
            argument = argument.split(',')
            return opfunc(field, argument)
    
    #Binary Operators accepting single argument
    else:
        opfunc = list(filter(
                                lambda e: hasattr(field, e % operator), 
                                ['%s','%s_','__%s__']
                            ))
        if not opfunc:
            raise UnknownOperator(msg="No operator found{0}".format(operator))
        opfunc = opfunc[0] % operator
        return getattr(field, opfunc)(argument)    

def create_filter(model, filt):
    if not isinstance(filt, JunctionFilter):
        fname = filt.fieldname
        val = filt.argument
        return create_operation(model, fname, filt.operator, val)
    if isinstance(filt, ConjunctionFilter):
        return and_(create_filter(model, f) for f in filt)
    return or_(create_filter(model, f) for f in filt)
