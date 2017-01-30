import re
from mimerender import FlaskMimeRender
from mimerender import register_mime
from functools import wraps
from flask import request, json, jsonify
from .exception import NotAcceptable, MediaTypeNotSupported
from werkzeug import parse_options_header

CONTENT_TYPE = 'application/vnd.api+json'

JSONAPI_VERSION = '1.0'

ACCEPT_RE = re.compile(
    r'''(                       # media-range capturing-parenthesis
          [^\s;,]+              # type/subtype
          (?:[ \t]*;[ \t]*      # ";"
            (?:                 # parameter non-capturing-parenthesis
              [^\s;,q][^\s;,]*  # token that doesn't start with "q"
            |                   # or
              q[^\s;,=][^\s;,]* # token that is more than just "q"
            )
          )*                    # zero or more parameters
        )                       # end of media-range
        (?:[ \t]*;[ \t]*q=      # weight is a "q" parameter
          (\d*(?:\.\d+)?)       # qvalue capturing-parentheses
          [^,]*                 # "extension" accept params: who cares?
        )?                      # accept params are optional
    ''', re.VERBOSE)

"""View function decorators"""
def requires_json_api_accept(func):
    @wraps(func)
    def new_func(*args, **kw):
        header = request.headers.get('Accept')
        if header is None:
            return func(*args, **kw)
        header_pairs = list(parse_accept_header(header))
        if len(header_pairs) == 0:
            return func(*args, **kw)
        jsonapi_pairs = [(name, extra) for name, extra in header_pairs
                         if name.startswith(CONTENT_TYPE)]
        if len(jsonapi_pairs) == 0:
            detail = ('Accept header, if specified, must be the JSON API media type: {0}'.format(CONTENT_TYPE))
            raise NotAcceptable(msg=detail)
        if all(extra is not None for name, extra in jsonapi_pairs):
            detail = ('Accept header contained JSON API content type, but each'
                      ' instance occurred with media type parameters; at least'
                      ' one instance must appear without parameters (the part'
                      ' after the semicolon)')
            raise NotAcceptable(msg=detail)
        return func(*args, **kw)
    return new_func


def requires_json_api_mimetype(func):
    @wraps(func)
    def new_func(*args, **kw):
        if request.method not in ('PATCH', 'POST'):
            return func(*args, **kw)
        header = request.headers.get('Content-Type')
        content_type, extra = parse_options_header(header)
        content_is_json = content_type.startswith(CONTENT_TYPE)
        if not content_is_json:
            detail = ('Request must have "Content-Type: {0}"'
                      ' header').format(CONTENT_TYPE)
            raise MediaTypeNotSupported(msg=detail)
        if extra:
            detail = ('Content-Type header must not have any media type'
                      ' parameters but found {0}'.format(extra))
            raise MediaTypeNotSupported(msg=detail)
        return func(*args, **kw)
    return new_func

def parse_accept_header(value):
    def match_to_pair(match):
        name = match.group(1)
        extra = match.group(2)
        quality = max(min(float(extra), 1), 0) if extra else None
        return name, quality
    return map(match_to_pair, ACCEPT_RE.finditer(value))
###############################################################################################################################


"""Mimerender initilization"""  
def create_json_response(*args, **kw):
    headers = kw['meta'].pop(_HEADERS, {}) if 'meta' in kw else {}
    status_code = kw['meta'].pop(_STATUS, 200) if 'meta' in kw else 200
    response = jsonify(*args, **kw)
    if 'Content-Type' not in headers:
        headers['Content-Type'] = CONTENT_TYPE
    if headers:
        for key, value in headers.items():
            response.headers.set(key, value)
    response.status_code = status_code
    return response

#register_mime('jsonapi', (CONTENT_TYPE, ))
#mimerender = FlaskMimeRender()(default = 'jsonapi', jsonapi = create_json_response)
####################################################################################################################################


