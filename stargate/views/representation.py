from flask import request, make_response, jsonify, json
from ..proxy import manager_info, URL_FOR, SERIALIZER_FOR
from ..pagination_links import PaginationLinks

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
        
        self_link = "{0}{1}?".format(request.url_root, manager_info(URL_FOR, self.model).lstrip('/'))
        self_link = PaginationLinks.get_paginated_url(self_link, self.page_number, self.page_size)
        self.__base_repr__['data'] = self.data
        self.__base_repr__['num_results'] = self.num_results
        self.__base_repr__['links'] = PaginationLinks.get_pagination_links(self.page_size, self.page_number, self.num_results, self.first, self.last, self.next, self.prev)
        self.__base_repr__['meta']['_HEADERS']['rel'] = self_link
        
        return super(CollectionRepresentation,self).to_response()
