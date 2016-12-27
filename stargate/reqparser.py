from .entity_manager.query_filter import QueryUtils
from .entity_manager.parser import Parser
import urllib.parse as urlparse
from functools import wraps

class ReqParser(object):

	def __init__(self, request):
		self.current_request = request

	def parse_query_str(self):
		def decorator(func):
			query_string = self.current_request['QUERY_STRING'].strip()
			query_string_dict = dict(urlparse.parse_qs(query_string, encoding = 'utf-8'))
			return ReqParser._parse_filter_expression(query_string_dict)
		return decorator

	def _parse_filter_expression(query_string_dict):
		
		if 'fields' in query_string_dict:
			fields = query_string_dict['fields'][0]
			query_fields = QueryUtils.get_query_element_list(model, fields, 'fields')
		
		if 'embed' in query_string_dict:
			entities = query_string_dict['embed'][0]
			query_embed = QueryUtils.get_query_element_list(model, entities, 'embed')

		if 'embed_inner' in query_string_dict:
			inner_entities = query_string_dict['embed_inner'][0]
			query_embed_inner = QueryUtils.get_query_element_list(model, inner_entities, 'embed_inner')

		if 'filters' in query_string_dict:
			filter_str = query_string_dict['filters'][0]
			group_filters, simple_filters = Parser.parse_filters(filter_str)
			query_filters = QueryFilter.create_filters({'priority_filters': group_filters, 'simple_filters': simple_filters}, model)

		if 'sort' in query_string_dict:
			sort_str = query_string_dict['sort'][0]
			query_order = QueryUtils.get_query_element_list(model, sort_str, 'sort')

		if 'offset' in query_string_dict:
			offset = query_string_dict['offset'][0]

		if 'page_size' in query_string_dict:
			page_size = query_string_dict['page_size'][0]
