from flask import request, make_response, jsonify
from ..proxy import serializer_for, url_for

class Representation():
    
    __base_repr__ = {'meta':{'status_code':None, 'message':None, '_HEADERS':{'Content-Type':'application/vnd.api+json'}}}
    
    _response_message={200: 'Ok.'}

    def __init__(self, code, message = None, content_type=None, headers={}):

        self.__base_repr__['meta']['status_code'] = code
        self.__base_repr__['meta']['message'] = self._response_message[code] if message is None else message
        self.__base_repr__['meta']['_HEADERS'].update(headers)

    def to_response(self):
        
        headers = self.__base_repr__['meta'].pop('_HEADERS', {}) if 'meta' in self.__base_repr__ else {}
        response = make_response(jsonify(self.__base_repr__))
        if headers:
            for key, value in headers.items():
                response.headers.set(key, value)
        return response

class InstanceRepresentation(Representation):
    
    def __init__(self, model, pk_id, instance, *args, **kw):
        
        super(InstanceRepresentation, self).__init__(*args, **kw)
        self.model = model
        self.pk_id = pk_id
        self.instance = instance

    def to_response(self):

        self_link = url_for(self.model, self.pk_id, _method='GET')
        serializer = serializer_for(self.model)
        data = serializer(self.instance)
        
        self.__base_repr__['meta']['_HEADERS']['rel'] = self_link
        self.__base_repr__['data'] = data
        return super(InstanceRepresentation,self).to_response()
               

class CollectionRepresentation(Representation):
    
    def __init__(self, model, page_size, pagination, *args, **kw):
        
        super(CollectionRepresentation, self).__init__(200,*args, **kw)

        self.num_results = pagination.total
        self.first = 1
        self.last = pagination.pages
        self.prev = pagination.prev_num
        self.next = pagination.next_num
        self.items = pagination.items
        self.page_size = page_size
        self.model = model

    def to_response(self):
        
        serializer = serializer_for(self.model)
        data = serializer(self.items)
        
        self.__base_repr__['data'] = data
        self.__base_repr__['num_results'] = self.num_results
        self.__base_repr__['links'] = self._pagination_links()
        
        return super(CollectionRepresentation,self).to_response()

    def _pagination_links(self):

        LINK_NAMES = ('first', 'last', 'prev', 'next')
        
        link_url = self._url_without_pagination_params()
        
        first = "{0}&page_number={1}&page_size={2}".format(link_url,self.first,self.page_size)
        last = "{0}&page_number={1}&page_size={2}".format(link_url,self.last,self.page_size)
        next = "{0}&page_number={1}&page_size={2}".format(link_url,self.next,self.page_size)
        prev = "{0}&page_number={1}&page_size={2}".format(link_url,self.prev,self.page_size)

        return {'first': first, 'last': last, 'next': next, 'prev': prev}

    def _url_without_pagination_params(self):
        base_url = request.base_url
        query_params = request.args
        new_query = dict((k, v) for k, v in query_params.items()
                         if k not in ('page_number', 'page_size'))
        new_query_string = '&'.join(map('='.join, new_query.items()))
        return '{0}?{1}'.format(base_url, new_query_string)
