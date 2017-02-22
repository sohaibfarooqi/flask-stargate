from flask import request, make_response, jsonify, json
from ..proxy import manager_info, URL_FOR, SERIALIZER_FOR
import math

class Representation():
        
    _response_message={200: 'Ok.'}

    def __init__(self, code, message = None, content_type=None, headers={}):
        self.__base_repr__ = {'meta':{'status_code':None, 'message':None, '_HEADERS':{'Content-Type':'application/vnd.api+json'}}}
        self.__base_repr__['meta']['status_code'] = code
        self.__base_repr__['meta']['message'] = self._response_message[code] if message is None else message
        self.__base_repr__['meta']['_HEADERS'].update(headers)

    def to_response(self):
        
        headers = self.__base_repr__['meta'].pop('_HEADERS', {}) if 'meta' in self.__base_repr__ else {}
        settings = {}
        settings.setdefault('indent', 4)
        settings.setdefault('sort_keys', True)
        response_doc = json.dumps(self.__base_repr__, **settings)
        response = make_response(response_doc)
        if headers:
            for key, value in headers.items():
                response.headers.set(key, value)
        return response

class InstanceRepresentation(Representation):
    
    def __init__(self, model, pk_id, data, *args, **kw):
        
        super(InstanceRepresentation, self).__init__(*args, **kw)
        self.model = model
        self.pk_id = pk_id
        self.data = data

    def to_response(self):

        self_link = manager_info(URL_FOR, self.model, pk_id = self.pk_id)
        
        self.__base_repr__['meta']['_HEADERS']['rel'] = self_link
        self.__base_repr__['data'] = self.data
        return super(InstanceRepresentation,self).to_response()
               

class CollectionRepresentation(Representation):
    
    def __init__(self, model, page_size, page_number, pagination, data,*args, **kw):
        
        super(CollectionRepresentation, self).__init__(200,*args, **kw)

        self.num_results = pagination.total
        self.first = 1
        self.last = pagination.pages
        self.prev = pagination.prev_num
        self.next = pagination.next_num
        self.data = data
        self.page_size = page_size
        self.page_number = page_number
        self.model = model

    def to_response(self):
        self_link = manager_info(URL_FOR, self.model)
        self_link = self._url_without_pagination_params()
        self_link = self._get_paginated_url(self_link, self.page_number, self.page_size)
        self.__base_repr__['data'] = self.data
        self.__base_repr__['num_results'] = self.num_results
        self.__base_repr__['links'] = self._pagination_links()
        self.__base_repr__['meta']['_HEADERS']['rel'] = self_link
        return super(CollectionRepresentation,self).to_response()

    def _pagination_links(self):

        LINK_NAMES = ('first', 'last', 'prev', 'next')
        
        link_url = self._url_without_pagination_params()
        
        if self.num_results == 0:
            last = 1
        
        else:
            last = int(math.ceil(self.num_results / self.page_size))
        
        prev = self.page_number - 1 if self.page_number > 1 else None
        next = self.page_number + 1 if self.page_number < last else None
            
        first = self._get_paginated_url(link_url,self.first,self.page_size)
        last = self._get_paginated_url(link_url,self.last,self.page_size)
        
        if next is not None:
            next = self._get_paginated_url(link_url,self.next,self.page_size)
        
        if prev is not None:
            prev = self._get_paginated_url(link_url,self.prev,self.page_size)

        return {'first': first, 'last': last, 'next': next, 'prev': prev}

    def _url_without_pagination_params(self):
        base_url = request.base_url
        query_params = request.args
        new_query = dict((k, v) for k, v in query_params.items()
                         if k not in ('page_number', 'page_size'))
        new_query_string = '&'.join(map('='.join, new_query.items()))
        return '{0}?{1}'.format(base_url, new_query_string)

    def _get_paginated_url(self, link, page_number, page_size):
        
        if link.endswith('?'):
            return "{0}page_number={1}&page_size={2}".format(link, page_number, page_size)
        
        else:
            return "{0}&page_number={1}&page_size={2}".format(link, page_number, page_size)
