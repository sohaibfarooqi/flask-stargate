from flask import Flask, Request
from werkzeug.urls import url_decode
from werkzeug._compat import wsgi_get_bytes
import urllib.parse as urlparse
from .negotiation import DefaultNegotiation
from .setting import default_settings
from werkzeug.urls import url_decode_stream
from werkzeug.wsgi import get_content_length
from werkzeug._compat import to_unicode
from werkzeug.datastructures import MultiDict
import io
from .parser import JSONParser, MultiPartParser, URLEncodedParser, APIURLParser
from .renderer import JSONRenderer, HTMLRenderer, BrowsableAPIRenderer


class RequestCls(Request):
    """Request subclass to override request parameter storage"""
    
    parser_classes = [JSONParser, MultiPartParser, URLEncodedParser, APIURLParser]
    renderer_classes = [JSONRenderer, HTMLRenderer, BrowsableAPIRenderer]
    negotiator_class = DefaultNegotiation
    empty_data_class = MultiDict
    
    @property
    def args(self):
        query_str = self.environ.get('QUERY_STRING', '')
        if query_str is not None:
            self._parse_query_str(query_str)
            return self._args

        else:
            return None

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._parse()
        return self._data
	
    @property
    def form(self):
        if not hasattr(self, '_form'):
            self._parse()
        return self._form

    @property
    def files(self):
        if not hasattr(self, '_files'):
            self._parse()
        return self._files

    def _parse_query_str(self, query_str):

        if not self.content_type:
            self._set_empty_data()
            return

        negotiator = self.negotiator_class()
        parsers = [parser_cls() for parser_cls in self.parser_classes]
        options = self._get_parser_options()
        try:
            parser, media_type = negotiator.select_parser(parsers)
            self._args = parser.parse(query_str, media_type, **options)
        except:
            # Ensure that accessing `request.data` again does not reraise
            # the exception, so that eg exceptions can handle properly.
            self._set_empty_data()
            raise

    def _parse(self):
        """
        Parse the body of the request, using whichever parser satifies the
        client 'Content-Type' header.
        """
        if not self.content_type or not self.content_length:
            self._set_empty_data()
            return

        negotiator = self.negotiator_class()
        parsers = [parser_cls() for parser_cls in self.parser_classes]
        options = self._get_parser_options()
        try:
            parser, media_type = negotiator.select_parser(parsers)
            ret = parser.parse(self.stream, media_type, **options)
        except:
            # Ensure that accessing `request.data` again does not reraise
            # the exception, so that eg exceptions can handle properly.
            self._set_empty_data()
            raise

        if query_str is not None:
            self._args = ret
        
        elif parser.handles_file_uploads:
            assert isinstance(ret, tuple) and len(ret) == 2, 'Expected a two-tuple of (data, files)'
            self._data, self._files = ret
        else:
            self._data = ret
            self._files = self.empty_data_class()

        self._form = self._data if parser.handles_form_data else self.empty_data_class()

    def _get_parser_options(self):

        """Any additional information to pass to the parser."""
        return {'content_length': self.content_length}

    def _set_empty_data(self):
        """
        If the request does not contain data then return an empty representation.
        """
        self._data = self.empty_data_class()
        self._form = self.empty_data_class()
        self._files = self.empty_data_class()

    # Content negotiation...

    @property
    def accepted_renderer(self):
        if not hasattr(self, '_accepted_renderer'):
            self._perform_content_negotiation()
        return self._accepted_renderer

    @property
    def accepted_media_type(self):
        if not hasattr(self, '_accepted_media_type'):
            self._perform_content_negotiation()
        return self._accepted_media_type

    def _perform_content_negotiation(self):
        """
        Determine which of the available renderers should be used for
        rendering the response content, based on the client 'Accept' header.
        """
        negotiator = self.negotiator_class()
        renderers = [renderer() for renderer in self.renderer_classes]
        self._accepted_renderer, self._accepted_media_type = negotiator.select_renderer(renderers)

    # Method and content type overloading.

    @property
    def method(self):
        if not hasattr(self, '_method'):
            self._perform_method_overloading()
        return self._method

    @property
    def content_type(self):
        if not hasattr(self, '_content_type'):
            self._perform_method_overloading()
        return self._content_type

    @property
    def content_length(self):
        if not hasattr(self, '_content_length'):
            self._perform_method_overloading()
        return self._content_length

    @property
    def stream(self):
        if not hasattr(self, '_stream'):
            self._perform_method_overloading()
        return self._stream

    def _perform_method_overloading(self):
        """
        Perform method and content type overloading.

        Provides support for browser PUT, PATCH, DELETE & other requests,
        by specifing a '_method' form field.

        Also provides support for browser non-form requests (eg JSON),
        by specifing '_content' and '_content_type' form fields.
        """
        self._method = super(RequestCls, self).method
        self._stream = super(RequestCls, self).stream
        self._content_type = self.headers.get('Content-Type')
        self._content_length = get_content_length(self.environ)

        if (self._method == 'POST' and self._content_type == 'application/x-www-form-urlencoded'):
            # Read the request data, then push it back onto the stream again.
            body = self.get_data()
            data = url_decode_stream(io.BytesIO(body))
            self._stream = io.BytesIO(body)
            if '_method' in data:
                # Support browser forms with PUT, PATCH, DELETE & other methods.
                self._method = data['_method']
            if '_content' in data and '_content_type' in data:
                # Support browser forms with non-form data, such as JSON.
                body = data['_content'].encode('utf8')
                self._stream = io.BytesIO(body)
                self._content_type = data['_content_type']
                self._content_length = len(body)

    # Misc...

    @property
    def full_path(self):
        """
        Werzueg's full_path implementation always appends '?', even when the
        query string is empty.  Let's fix that.
        """
        if not self.query_string:
            return self.path
        return self.path + u'?' + to_unicode(self.query_string, self.url_charset)