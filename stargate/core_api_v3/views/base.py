from itertools import chain
from flask.views import MethodView
from flask import request, json
from ..proxy import collection_name_for
from collections import defaultdict
from sqlalchemy.exc import SQLAlchemyError
from .query_helper.search import Search
from .query_helper.pagination import SimplePagination
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from ..exception import SerializationException, SingleKeyError, StargateException, ResourceNotFound
from ..errors import catch_processing_exceptions, catch_integrity_errors
from ..mimerender import requires_json_api_accept, requires_json_api_mimetype, mimerender

FILTER_PARAM = 'filter[objects]'
SORT_PARAM = 'sort'
GROUP_PARAM = 'group'
PAGE_NUMBER_PARAM = 'page[number]'
PAGE_SIZE_PARAM = 'page[size]'
SINGLE_RESOURCE_PARAM = 'filter[single]'

chain = chain.from_iterable


"""Utility functions"""
def upper_keys(dictionary):
    return dict((k.upper(), v) for k, v in dictionary.items())

def parse_sparse_fields(type_=None):
        fields = dict((key[7:-1], set(value.split(',')))
                  for key, value in request.args.items()
                  if key.startswith('fields[') and key.endswith(']'))
        return fields.get(type_) if type_ is not None else fields
#######################################################################################################

class BaseAPI(MethodView):
    
    decorators = [  
                    requires_json_api_accept, 
                    requires_json_api_mimetype,
                    mimerender,
                    catch_processing_exceptions
                 ]
    def __init__(self, session, model, preprocessors=None, postprocessors=None,
                 primary_key=None, serializer=None, deserializer=None,
                 validation_exceptions=None, includes=None, page_size=10,
                 max_page_size=100, allow_to_many_replacement=False, *args,
                 **kw):

        super(BaseAPI, self).__init__()
        self.collection_name = collection_name_for(model)
        
        self.default_includes = includes
        if self.default_includes is not None:
            self.default_includes = frozenset(self.default_includes)

        self.session = session
        self.model = model

        self.allow_to_many_replacement = allow_to_many_replacement

        self.page_size = page_size

        self.max_page_size = max_page_size

        self.serialize = serializer

        self.deserialize = deserializer

        self.validation_exceptions = tuple(validation_exceptions or ())

        self.primary_key = primary_key

        self.postprocessors = defaultdict(list, upper_keys(postprocessors or {}))

        self.preprocessors = defaultdict(list, upper_keys(preprocessors or {}))

        self.sparse_fields = parse_sparse_fields()

        # decorate = lambda name, f: setattr(self, name, f(getattr(self, name)))
        # for method in ['get', 'post', 'patch', 'delete']:
        #     if hasattr(self, method):
        #         decorate(method, catch_integrity_errors(self.session))
   
    

    def _collection_filter_parameters(self):

        query_string = request.args.to_dict()
        
        filters = query_string['filters']
        sort = query_string['sort']
        group_by = query_string['group']
        single = query_string['single']
        include = query_string['include']
        fields = query_string['fields']
        
        filters = json.loads(query_string)

        if sort:
            sort = [('-', value[1:]) if value.startswith('-') else ('+', value)
                    for value in sort.split(',')]
        else:
            sort = []

        if group_by:
            group_by = group_by.split(',')
        else:
            group_by = []

        try:
            single = bool(int(request.args.get(SINGLE_RESOURCE_PARAM, 0)))
        except ValueError:
            raise SingleKeyError('failed to extract Boolean from parameter')

        return filters, sort, group_by, single

    
    def _get_collection(self,filters=None, sort=None, group_by=None,
                               single=False):
        try:
            search_items = Search(self.session, self.model, filters=filters, sort=sort,
                                   group_by=group_by)
        except Exception as exception:
            detail = 'Unable to construct query'
            return StargateException(msg=detail)

        #collection
        if not single:
            paginated = SimplePagination.simple_pagination(search_items.search_collection(),filters = filters, sort = sort, group_by = group_by)
            data = paginated.items
            links = paginated.pagination_links
            header = ','.join(paginated.header_links)
            link_header = dict(Link = header)
            num_results = paginated.num_results
            single = single
        
        #Force single
        else:
            try:
                data = search_items.search_collection().one()
            except NoResultFound as exception:
                detail = 'No result found'
                raise ResourceNotFound(self.model.__name__(), msg=detail)
            except MultipleResultsFound as exception:
                detail = 'Multiple results found'
                raise StargateException(msg=detail)
            
            serialize = self.serialize
            # result['data'] = serialize(data, only=only)
            result['data'] = serialize(data)
            
            #Link Header Generation
            primary_key = primary_key_for(data)
            pk_value = result['data'][primary_key]
            url = '{0}/{1}'.format(request.base_url, pk_value)
            headers = dict(Location=url)

            link_header = headers
            single = single

            
        result = {'data': data, 'link_header': link_header, 'links': links, 'num_results': num_results,'include': inclusions, 'single': 'single'}
        
        return result
