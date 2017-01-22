from flask import request, json
from ..base_collection import FILTER_PARAM, SORT_PARAM, PAGE_SIZE_PARAM, PAGE_NUMBER_PARAM, GROUP_PARAM

LINK_NAMES = ('first', 'last', 'prev', 'next')

class PaginationError(Exception):
    pass

class Pagination(object):
    
    def __init__(self, items):
        self._items = items
        self._num_results = num_results
        self._pagination_links = {}
        self._header_links = []
        query_params = {}
        if filters:
            query_params[FILTER_PARAM] = Pagination._filters_to_string(filters)
        if sort:
            query_params[SORT_PARAM] = Pagination._sort_to_string(sort)
        if group_by:
            query_params[GROUP_PARAM] = Pagination._group_to_string(group_by)
        query_params[PAGE_SIZE_PARAM] = str(page_size)
        link_numbers = [first, last, prev, next_]
        base_url = Pagination._url_without_pagination_params()
        for rel, num in zip(LINK_NAMES, link_numbers):
            if num is None:
                self._pagination_links[rel] = None
            else:
                query_params[PAGE_NUMBER_PARAM] = str(num)
                url = Pagination._to_url(base_url, query_params)
                link_string = '<{0}>; rel="{1}"'.format(url, rel)
                self._header_links.append(link_string)
                self._pagination_links[rel] = url

    def simple_pagination(first=None, last=None, prev=None, next_=None,
                        page_size=None, num_results=None, filters=None, sort=None,
                        group_by=None):
        pass

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


    def _paginated(self, items, filters=None, sort=None, group_by=None):
        page_size = int(request.args.get(PAGE_SIZE_PARAM, self.page_size))
        if page_size < 0:
            raise PaginationError('Page size must be a positive integer')
        if page_size > self.max_page_size:
            msg = "Page size must not exceed the server's maximum: {0}"
            msg = msg.format(self.max_page_size)
            raise PaginationError(msg)
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
        
        for item in items:
            model = get_model(instance)
            
            try:
                serialize = serializer_for(model)
            except ValueError:
                    serialize = self.serialize
            
            try:
                serialized = serialize(instance, only=only)
                result.append(serialized)
            except SerializationException as exception:
                pass
        return Paginated(result, num_results=num_results, first=first,
                         last=last, next_=next_, prev=prev,
                         page_size=page_size, filters=filters, sort=sort,
                         group_by=group_by)
        