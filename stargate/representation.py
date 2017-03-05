"""Representation class for API. Provides Collection, and Instance representation according to API format.
Provides data, links, link header etc. Custom headers can be injected by using `_HEADERS` inside `meta` key.

"""
from flask import request, make_response, jsonify, json
from .resource_info import resource_info
from .utils import get_paginated_url, get_pagination_links
from .const import ResourceInfoConst, SerializationConst, MediatypeConstants

class Representation():
    """Response Representation class. This class is used in view functions to generate appropriate
    response according to client `Accept` Header. Any additional header that needs to be appended to
    response can be pass like {'meta':{"_HEADERS":{"X_AUTH_KEY": "abcde"}}}`. This class will pop 
    all key within `_HEADER` key and add them to response object. It also provide `status message`
    according to HTTP status code passed to initilize class object.

    :param code: HTTP status code.
    :param message: Status message if any.
    :param content_type: Content Type for response. 
    :param headers: Additional Headers. 
        
      """  
    _response_message = {200: 'Ok.', 201: "Created", 204: "No Content"}

    def __init__(self, code, message = None, content_type=None, headers={}):
        
        self.__base_repr__ = {'meta':{'status_code':None, 'message':None, '_HEADERS':{'Content-Type':MediatypeConstants.CONTENT_TYPE}}}
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
    """This class override default Representation class to provide Instance Representation
    according to API specification.

    :param model: Resource Model Class.
    :param pk_id: Primary key id for resource.
    :param data: Serialized data. 
    :param *args: Additional list arguments for Parent class. 
    :param **kw: Additional key word arguments for Parent class.

    """
    def __init__(self, model, pk_id, data, *args, **kw):
        
        super(InstanceRepresentation, self).__init__(*args, **kw)
        self.model = model
        self.pk_id = pk_id
        self.data = data

    def to_response(self):

        self_link = resource_info(ResourceInfoConst.URL_FOR, self.model, pk_id = self.pk_id)
        
        self.__base_repr__['meta']['_HEADERS']['rel'] = self_link
        self.__base_repr__[SerializationConst.DATA] = self.data
        return super(InstanceRepresentation,self).to_response()
               

class CollectionRepresentation(Representation):
    """This class override default Representation class to provide Collection Representation
    according to API specification.

    :param model: Resource Model Class.
    :param data: Serialized collection data. 
    :param *args: Additional list arguments for Parent class. 
    :param **kw: Additional key word arguments for Parent class.

    """
    def __init__(self, model, data, *args, **kw):
        
        super(CollectionRepresentation, self).__init__(*args, **kw)
        self.data = data
        self.model = model

    def to_response(self, page_size = None, page_number = None, pagination = None):
        
        self_link =  resource_info(ResourceInfoConst.URL_FOR, self.model)
        
        if pagination is not None and page_number is not None and page_size is not None:
            num_results = pagination.total
            first = 1
            last = pagination.pages
            prev = pagination.prev_num
            next = pagination.next_num
            page_size = page_size
            page_number = page_number
        
            self_link = get_paginated_url(self_link, page_number, page_size)
            self.__base_repr__[SerializationConst.NUM_RESULTS] = num_results
            self.__base_repr__[SerializationConst.LINKS] = get_pagination_links(page_size, page_number, num_results, first, last, next, prev)
        
        self.__base_repr__['meta']['_HEADERS']['rel'] = self_link
        self.__base_repr__[SerializationConst.DATA] = self.data
        
        return super(CollectionRepresentation,self).to_response()
