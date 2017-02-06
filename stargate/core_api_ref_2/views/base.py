from __future__ import division

from collections import defaultdict
from functools import partial
from functools import wraps
from itertools import chain
import math
import re
from urllib.parse import urlparse
from urllib.parse import urlunparse
from flask import current_app
from flask import json
from flask import jsonify
from flask import request
from flask.views import MethodView
from mimerender import FlaskMimeRender
from mimerender import register_mime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.query import Query
from werkzeug import parse_options_header
from werkzeug.exceptions import HTTPException

from ..helpers import collection_name
from ..helpers import get_model
from ..helpers import is_like_list
from ..helpers import primary_key_for
from ..helpers import primary_key_value
from ..helpers import serializer_for
from ..helpers import url_for
from ..search import ComparisonToNull
from ..search import search
from ..search import search_relationship
from ..search import UnknownField
from ..serialization import simple_serialize
from ..serialization import simple_relationship_serialize
from ..serialization import DefaultDeserializer
from ..serialization import DeserializationException
from ..serialization import SerializationException
from .helpers import count
from .helpers import upper_keys as upper

_HEADERS = '__restless_headers'

_STATUS = '__restless_status_code'

CONTENT_TYPE = 'application/vnd.api+json'

JSONAPI_VERSION = '1.0'

CONFLICT_INDICATORS = ('conflicts with', 'UNIQUE constraint failed',
                       'is not unique')

LINK_NAMES = ('first', 'last', 'prev', 'next')

FILTER_PARAM = 'filter[objects]'

SORT_PARAM = 'sort'

GROUP_PARAM = 'group'

PAGE_NUMBER_PARAM = 'page[number]'

PAGE_SIZE_PARAM = 'page[size]'

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

ERROR_FIELDS = ('id_', 'links', 'status', 'code_', 'title', 'detail', 'source',
                'meta')

chain = chain.from_iterable

register_mime('jsonapi', (CONTENT_TYPE, ))


class SingleKeyError(KeyError):
    pass


class PaginationError(Exception):
    pass


class ProcessingException(HTTPException):

    def __init__(self, id_=None, links=None, status=400, code=None, title=None,
                 detail=None, source=None, meta=None, *args, **kw):
        super(ProcessingException, self).__init__(*args, **kw)
        self.id_ = id_
        self.links = links
        self.status = status
        self.code_ = code
        self.code = status
        self.title = title
        self.detail = detail
        self.source = source
        self.meta = meta


class MultipleExceptions(Exception):

    def __init__(self, exceptions, *args, **kw):
        super(MultipleExceptions, self).__init__(*args, **kw)
        self.exceptions = exceptions


def _is_msie8or9():
    version = lambda ua: tuple(int(d) for d in ua.version.split('.'))
    return (request.user_agent is not None
            and request.user_agent.version is not None
            and request.user_agent.browser == 'msie'
            and (8, 0) <= version(request.user_agent) < (10, 0))


def un_camel_case(s):
    return re.sub(r'(?<=\w)([A-Z])', r' \1', s)


def catch_processing_exceptions(func):
    @wraps(func)
    def new_func(*args, **kw):
        try:
            return func(*args, **kw)
        except ProcessingException as exception:
            kw = dict((key, getattr(exception, key)) for key in ERROR_FIELDS)
            kw['code'] = kw.pop('code_')
            return error_response(cause=exception, **kw)
    return new_func


def parse_accept_header(value):
    def match_to_pair(match):
        name = match.group(1)
        extra = match.group(2)
        quality = max(min(float(extra), 1), 0) if extra else None
        return name, quality
    return map(match_to_pair, ACCEPT_RE.finditer(value))


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
            detail = ('Accept header, if specified, must be the JSON API media'
                      ' type: application/vnd.api+json')
            return error_response(406, detail=detail)
        if all(extra is not None for name, extra in jsonapi_pairs):
            detail = ('Accept header contained JSON API content type, but each'
                      ' instance occurred with media type parameters; at least'
                      ' one instance must appear without parameters (the part'
                      ' after the semicolon)')
            return error_response(406, detail=detail)
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
        is_msie = _is_msie8or9()
        if not is_msie and not content_is_json:
            detail = ('Request must have "Content-Type: {0}"'
                      ' header').format(CONTENT_TYPE)
            return error_response(415, detail=detail)
        if extra:
            detail = ('Content-Type header must not have any media type'
                      ' parameters but found {0}'.format(extra))
            return error_response(415, detail=detail)
        return func(*args, **kw)
    return new_func


def catch_integrity_errors(session):
    
    def decorated(func):
        @wraps(func)
        def wrapped(*args, **kw):
            try:
                return func(*args, **kw)
            except SQLAlchemyError as exception:
                session.rollback()
                status = 409 if is_conflict(exception) else 400
                detail = str(exception)
                title = un_camel_case(exception.__class__.__name__)
                return error_response(status, cause=exception, detail=detail,
                                      title=title)
        return wrapped
    return decorated


def is_conflict(exception):
    exception_string = str(exception)
    return any(s in exception_string for s in CONFLICT_INDICATORS)


def jsonpify(*args, **kw):
    headers = kw['meta'].pop(_HEADERS, {}) if 'meta' in kw else {}
    status_code = kw['meta'].pop(_STATUS, 200) if 'meta' in kw else 200
    response = jsonify(*args, **kw)
    callback = request.args.get('callback', False)
    if callback:
        document = json.loads(response.data)
        mimetype = 'application/javascript'
        headers['Content-Type'] = mimetype
        meta = {}
        meta['status'] = status_code
        if 'meta' in document:
            document['meta'].update(meta)
        else:
            document['meta'] = meta
        inner = json.dumps(document)
        content = '{0}({1})'.format(callback, inner)
        response = current_app.response_class(content, mimetype=mimetype)
    if 'Content-Type' not in headers:
        headers['Content-Type'] = CONTENT_TYPE
    if headers:
        for key, value in headers.items():
            response.headers.set(key, value)
    response.status_code = status_code
    return response


def parse_sparse_fields(type_=None):
    fields = dict((key[7:-1], set(value.split(',')))
                  for key, value in request.args.items()
                  if key.startswith('fields[') and key.endswith(']'))
    return fields.get(type_) if type_ is not None else fields


def resources_from_path(instance, path):
    if '.' in path:
        path = path.split('.')
    else:
        path = [path]
    seen = set()
    nextlevel = set([instance])
    first_time = True
    while nextlevel:
        thislevel = nextlevel
        nextlevel = set()
        if path:
            relation = path.pop(0)
        else:
            relation = None
        for resource in thislevel:
            if resource in seen:
                continue
            if first_time:
                first_time = False
            else:
                yield resource
            seen.add(resource)
            if relation is not None:
                if is_like_list(resource, relation):
                    update = nextlevel.update
                else:
                    update = nextlevel.add
                update(getattr(resource, relation))

def extract_error_messages(exception):
    if isinstance(exception, DeserializationException):
        return exception.args[0]
    if hasattr(exception, 'errors'):
        return exception.errors
    if hasattr(exception, 'message'):
        try:
            left, right = str(exception).rsplit(':', 1)
            left_bracket = left.rindex('[')
            right_bracket = right.rindex(']')
        except ValueError as exc:
            current_app.logger.exception(str(exc))
            return None
        msg = right[:right_bracket].strip(' "')
        fieldname = left[left_bracket + 1:].strip()
        return {fieldname: msg}
    return None


def error(id_=None, links=None, status=None, code=None, title=None,
          detail=None, source=None, meta=None):
    if all(kwvalue is None for kwvalue in locals().values()):
        raise ValueError('At least one of the arguments must not be None.')
    return {'id': id_, 'links': links, 'status': status, 'code': code,
            'title': title, 'detail': detail, 'source': source, 'meta': meta}


def error_response(status=400, cause=None, **kw):
    if cause is not None:
        current_app.logger.exception(str(cause))
    kw['status'] = status
    return errors_response(status, [error(**kw)])


def errors_response(status, errors):
    document = {'errors': errors, 'jsonapi': {'version': JSONAPI_VERSION},
                'meta': {_STATUS: status}}
    return document, status


def error_from_serialization_exception(exception, included=False):
    type_ = collection_name(get_model(exception.instance))
    id_ = primary_key_value(exception.instance)
    if exception.message is not None:
        detail = exception.message
    else:
        resource = 'included resource' if included else 'resource'
        detail = 'Failed to serialize {0} of type {1} and ID {2}'
        detail = detail.format(resource, type_, id_)
    return error(status=500, detail=detail)


def errors_from_serialization_exceptions(exceptions, included=False):
    _to_error = partial(error_from_serialization_exception, included=included)
    errors = list(map(_to_error, exceptions))
    return errors_response(500, errors)


mimerender = FlaskMimeRender()(default='jsonapi', jsonapi=jsonpify)


class Paginated(object):
    
    @staticmethod
    def _filters_to_string(filters):
        return json.dumps(filters)

    @staticmethod
    def _sort_to_string(sort):
        return ','.join(''.join((dir_, field)) for dir_, field in sort)

    @staticmethod
    def _group_to_string(group_by):
        return ','.join(group_by)

    @staticmethod
    def _url_without_pagination_params():
        base_url = request.base_url
        query_params = request.args
        new_query = dict((k, v) for k, v in query_params.items()
                         if k not in (PAGE_NUMBER_PARAM, PAGE_SIZE_PARAM))
        new_query_string = '&'.join(map('='.join, new_query.items()))
        return '{0}?{1}'.format(base_url, new_query_string)

    @staticmethod
    def _to_url(base_url, query_params):
        query_string = '&'.join(map('='.join, query_params.items()))
        scheme, netloc, path, params, query, fragment = urlparse(base_url)
        if query:
            query_string = '&'.join((query, query_string))
        parsed = (scheme, netloc, path, params, query_string, fragment)
        return urlunparse(parsed)

    def __init__(self, items, first=None, last=None, prev=None, next_=None,
                 page_size=None, num_results=None, filters=None, sort=None,
                 group_by=None):
        self._items = items
        self._num_results = num_results
        self._pagination_links = {}
        self._header_links = []
        if page_size == 0:
            return
        query_params = {}
        if filters:
            query_params[FILTER_PARAM] = Paginated._filters_to_string(filters)
        if sort:
            query_params[SORT_PARAM] = Paginated._sort_to_string(sort)
        if group_by:
            query_params[GROUP_PARAM] = Paginated._group_to_string(group_by)
        query_params[PAGE_SIZE_PARAM] = str(page_size)
        link_numbers = [first, last, prev, next_]
        base_url = Paginated._url_without_pagination_params()
        for rel, num in zip(LINK_NAMES, link_numbers):
            if num is None:
                self._pagination_links[rel] = None
            else:
                query_params[PAGE_NUMBER_PARAM] = str(num)
                url = Paginated._to_url(base_url, query_params)
                link_string = '<{0}>; rel="{1}"'.format(url, rel)
                self._header_links.append(link_string)
                self._pagination_links[rel] = url
        
    @property
    def header_links(self):
        return self._header_links

    @property
    def pagination_links(self):
        return self._pagination_links

    @property
    def items(self):
        return self._items

    @property
    def num_results(self):
        return self._num_results


class ModelView(MethodView):
    decorators = [requires_json_api_accept, requires_json_api_mimetype,
                  mimerender]

    def __init__(self, session, model, *args, **kw):
        super(ModelView, self).__init__(*args, **kw)
        self.session = session
        self.model = model


class APIBase(ModelView):
    decorators = [catch_processing_exceptions] + ModelView.decorators

    def __init__(self, session, model, preprocessors=None, postprocessors=None,
                 primary_key=None, serializer=None, deserializer=None,
                 validation_exceptions=None, includes=None, page_size=10,
                 max_page_size=100, allow_to_many_replacement=False, *args,
                 **kw):
        super(APIBase, self).__init__(session, model, *args, **kw)

        self.collection_name = collection_name(self.model)
        self.default_includes = includes
        if self.default_includes is not None:
            self.default_includes = frozenset(self.default_includes)

        self.allow_to_many_replacement = allow_to_many_replacement

        self.page_size = page_size

        self.max_page_size = max_page_size

        self.serialize = serializer

        self.serialize_relationship = simple_relationship_serialize

        self.deserialize = deserializer

        self.validation_exceptions = tuple(validation_exceptions or ())

        self.primary_key = primary_key

        self.postprocessors = defaultdict(list, upper(postprocessors or {}))

        self.preprocessors = defaultdict(list, upper(preprocessors or {}))

        self.sparse_fields = parse_sparse_fields()

        decorate = lambda name, f: setattr(self, name, f(getattr(self, name)))
        for method in ['get', 'post', 'patch', 'delete']:
            if hasattr(self, method):
                decorate(method, catch_integrity_errors(self.session))

    def collection_processor_type(self, *args, **kw):
        raise NotImplementedError

    def resource_processor_type(self, *args, **kw):
        raise NotImplementedError

    def use_resource_identifiers(self):
        return False

    def _handle_validation_exception(self, exception):
        self.session.rollback()
        errors = extract_error_messages(exception)
        if not errors:
            title = 'Validation error'
            return error_response(400, cause=exception, title=title)
        if isinstance(errors, dict):
            errors = [error(title='Validation error', status=400,
                            detail='{0}: {1}'.format(field, detail))
                      for field, detail in errors.items()]
        current_app.logger.exception(str(exception))
        return errors_response(400, errors)

    def _serialize_many(self, instances, relationship=False):
        result = []
        failed = []
        for instance in instances:
            model = get_model(instance)
            if relationship:
                serialize = self.serialize_relationship
            else:
                try:
                    serialize = serializer_for(model)
                except ValueError:
                    serialize = self.serialize
            _type = collection_name(model)
            only = self.sparse_fields.get(_type)
            try:
                serialized = serialize(instance, only=only)
                result.append(serialized)
            except SerializationException as exception:
                failed.append(exception)
        if failed:
            raise MultipleExceptions(failed)
        return result

    def get_all_inclusions(self, instance_or_instances):
        if isinstance(instance_or_instances, Query):
            to_include = set(chain(self.resources_to_include(resource)
                                   for resource in instance_or_instances))
        else:
            to_include = self.resources_to_include(instance_or_instances)
        return self._serialize_many(to_include)

    def _collection_parameters(self):
        filters = json.loads(request.args.get(FILTER_PARAM, '[]'))
        sort = request.args.get(SORT_PARAM)
        if sort:
            sort = [('-', value[1:]) if value.startswith('-') else ('+', value)
                    for value in sort.split(',')]
        else:
            sort = []

        group_by = request.args.get(GROUP_PARAM)
        if group_by:
            group_by = group_by.split(',')
        else:
            group_by = []

        try:
            single = bool(int(request.args.get('filter[single]', 0)))
        except ValueError:
            raise SingleKeyError('failed to extract Boolean from parameter')

        return filters, sort, group_by, single

    def _paginated(self, items, filters=None, sort=None, group_by=None):
        page_size = int(request.args.get(PAGE_SIZE_PARAM, self.page_size))
        if page_size < 0:
            raise PaginationError('Page size must be a positive integer')
        if page_size > self.max_page_size:
            msg = "Page size must not exceed the server's maximum: {0}"
            msg = msg.format(self.max_page_size)
            raise PaginationError(msg)
        is_relationship = self.use_resource_identifiers()
        if page_size == 0:
            result = self._serialize_many(items, relationship=is_relationship)
            num_results = len(result)
            return Paginated(result, page_size=page_size,
                             num_results=num_results)
        page_number = int(request.args.get(PAGE_NUMBER_PARAM, 1))
        if page_number < 0:
            raise PaginationError('Page number must be a positive integer')
        if hasattr(items, 'paginate'):
            pagination = items.paginate(page_number, page_size,
                                        error_out=False)
            num_results = pagination.total
            first = 1
            last = pagination.pages
            prev = pagination.prev_num
            next_ = pagination.next_num
            items = pagination.items
        else:
            num_results = count(self.session, items)
            first = 1
            if num_results == 0:
                last = 1
            else:
                last = int(math.ceil(num_results / page_size))
            prev = page_number - 1 if page_number > 1 else None
            next_ = page_number + 1 if page_number < last else None
            offset = (page_number - 1) * page_size
            items = items.limit(page_size).offset(offset)
        result = self._serialize_many(items, relationship=is_relationship)
        return Paginated(result, num_results=num_results, first=first,
                         last=last, next_=next_, prev=prev,
                         page_size=page_size, filters=filters, sort=sort,
                         group_by=group_by)

    def _get_resource_helper(self, resource, primary_resource=None,
                             relation_name=None, related_resource=False):
        is_relationship = self.use_resource_identifiers()
        if resource is None:
            data = None
        else:
            try:
                data = self._serialize_many([resource],
                                            relationship=is_relationship)
            except MultipleExceptions as e:
                return errors_from_serialization_exceptions(e.exceptions)
            data = data[0]
        result = {'jsonapi': {'version': JSONAPI_VERSION}, 'meta': {},
                  'links': {}, 'data': data}
        is_relation = primary_resource is not None
        is_related_resource = is_relation and related_resource
        if is_related_resource:
            resource_id = primary_key_value(primary_resource)
            related_resource_id = primary_key_value(resource)
            self_link = url_for(self.model, resource_id, relation_name,
                                related_resource_id)
            result['links']['self'] = self_link
        elif is_relation:
            resource_id = primary_key_value(primary_resource)
            if is_relationship:
                self_link = url_for(self.model, resource_id, relation_name,
                                    relationship=True)
                related_link = url_for(self.model, resource_id, relation_name)
                result['links']['self'] = self_link
                result['links']['related'] = related_link
            else:
                self_link = url_for(self.model, resource_id, relation_name)
                result['links']['self'] = self_link
        else:
            result['links']['self'] = url_for(self.model)

        try:
            included = self.get_all_inclusions(resource)
        except MultipleExceptions as e:
            return errors_from_serialization_exceptions(e.exceptions,
                                                        included=True)
        if included:
            result['included'] = included
        kw = {'is_relation': is_relation,
              'is_related_resource': is_related_resource}
        processor_type = 'GET_{0}'.format(self.resource_processor_type(**kw))
        for postprocessor in self.postprocessors[processor_type]:
            postprocessor(result=result)
        return result, 200

    def _get_collection_helper(self, resource=None, relation_name=None,
                               filters=None, sort=None, group_by=None,
                               single=False):
        if (resource is None) ^ (relation_name is None):
            raise ValueError('resource and relation must be both None or both'
                             ' not None')
        is_relation = resource is not None
        if is_relation:
            search_ = partial(search_relationship, self.session, resource,
                              relation_name)
        else:
            search_ = partial(search, self.session, self.model)
        try:
            search_items = search_(filters=filters, sort=sort,
                                   group_by=group_by)
        except ComparisonToNull as exception:
            detail = str(exception)
            return error_response(400, cause=exception, detail=detail)
        except UnknownField as exception:
            detail = 'Invalid filter object: No such field "{0}"'
            detail = detail.format(exception.field)
            return error_response(400, cause=exception, detail=detail)
        except Exception as exception:
            detail = 'Unable to construct query'
            return error_response(400, cause=exception, detail=detail)

        result = {'links': {'self': url_for(self.model)},
                  'jsonapi': {'version': JSONAPI_VERSION},
                  'meta': {}}

        if not single:
            try:
                paginated = self._paginated(search_items, filters=filters,
                                            sort=sort, group_by=group_by)
            except MultipleExceptions as e:
                return errors_from_serialization_exceptions(e.exceptions)
            except PaginationError as exception:
                detail = exception.args[0]
                return error_response(400, cause=exception, detail=detail)
            result['data'] = paginated.items
            result['links'].update(paginated.pagination_links)
            link_header = ','.join(paginated.header_links)
            headers = dict(Link=link_header)
            num_results = paginated.num_results
        else:
            try:
                data = search_items.one()
            except NoResultFound as exception:
                detail = 'No result found'
                return error_response(404, cause=exception, detail=detail)
            except MultipleResultsFound as exception:
                detail = 'Multiple results found'
                return error_response(404, cause=exception, detail=detail)
            only = self.sparse_fields.get(self.collection_name)
            try:
                if self.use_resource_identifiers():
                    serialize = self.serialize_relationship
                else:
                    serialize = self.serialize
                result['data'] = serialize(data, only=only)
            except SerializationException as exception:
                return errors_from_serialization_exceptions([exception])
            primary_key = primary_key_for(data)
            pk_value = result['data'][primary_key]
            url = '{0}/{1}'.format(request.base_url, pk_value)
            headers = dict(Location=url)
            num_results = 1

        if self.use_resource_identifiers():
            instances = resource
        else:
            instances = search_items
        try:
            included = self.get_all_inclusions(instances)
        except MultipleExceptions as e:
            return errors_from_serialization_exceptions(e.exceptions,
                                                        included=True)
        if included:
            result['included'] = included

        processor_type = \
            self.collection_processor_type(is_relation=is_relation)
        processor_type = 'GET_{0}'.format(processor_type)
        for postprocessor in self.postprocessors[processor_type]:
            postprocessor(result=result, filters=filters, sort=sort,
                          group_by=group_by, single=single)
        status = 200
        result['meta'][_HEADERS] = headers
        result['meta'][_STATUS] = status
        result['meta']['total'] = num_results
        return result, status, headers

    def resources_to_include(self, instance):
        toinclude = request.args.get('include')
        if toinclude is None and self.default_includes is None:
            return {}
        elif toinclude is None and self.default_includes is not None:
            toinclude = self.default_includes
        else:
            toinclude = set(toinclude.split(','))
        return set(chain(resources_from_path(instance, path)
                         for path in toinclude))
