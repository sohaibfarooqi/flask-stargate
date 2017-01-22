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
