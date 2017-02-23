from flask import request
import math

class PaginationLinks:

	def get_pagination_links(page_size, page_number, num_results, first, last, next, prev, url = None):

		LINK_NAMES = ('first', 'last', 'prev', 'next')
	
		if url is not None:
			link_url = "{0}{1}?".format(request.url_root, url)	
		else:
			link_url = PaginationLinks._url_without_pagination_params(request.base_url)

		if num_results == 0:
			last = 1

		else:
			last = int(math.ceil(num_results / page_size))

		prev = page_number - 1 if page_number > 1 else None
		next = page_number + 1 if page_number < last else None

		first = PaginationLinks.get_paginated_url(link_url,first,page_size)
		last = PaginationLinks.get_paginated_url(link_url,last,page_size)

		if next is not None:
			next = PaginationLinks.get_paginated_url(link_url,next,page_size)

		if prev is not None:
			prev = PaginationLinks.get_paginated_url(link_url,prev,page_size)

		return {'first': first, 'last': last, 'next': next, 'prev': prev}
	
	def _url_without_pagination_params(url):
		base_url = url 
		query_params = request.args
		new_query = dict((k, v) for k, v in query_params.items()
							if k not in ('page_number', 'page_size'))
		new_query_string = '&'.join(map('='.join, new_query.items()))
		return '{0}?{1}'.format(base_url, new_query_string)

	def get_paginated_url(link, page_number, page_size):

		if link.endswith('?'):
			return "{0}page_number={1}&page_size={2}".format(link, page_number, page_size)

		else:
			return "{0}&page_number={1}&page_size={2}".format(link, page_number, page_size)
