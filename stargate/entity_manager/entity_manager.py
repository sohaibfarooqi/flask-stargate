from .models import Entity
import urllib.parse as urlparse
from .query_filter import QueryFilter, QueryFields, QueryOrder
from .parser import Parser

class EntityManager():

	def get(model, pk_id, query_string):
	
		if pk_id is None:
			
			query_string_dict = dict(urlparse.parse_qs(query_string, encoding = 'utf-8'))
			
			if 'filters' in query_string_dict:
				filter_str = query_string_dict['filters'][0]
			
			if 'sort' in query_string_dict:
				sort_str = query_string_dict['sort'][0]
			
			if 'fields' in query_string_dict:
				fields = query_string_dict['fields'][0]

			group_filters, simple_filters = Parser.parse_filters(filter_str)
			query_filters = QueryFilter.create_filters({'priority_filters': group_filters, 'simple_filters': simple_filters}, model)
			
			query_fields = QueryFields.get_field_list(fields, model)

			query_order = QueryOrder.get_order_by_list(sort_str, model)

			return Entity.get_collection(model, query_filters, query_fields, query_order)

		else:
			return Entity.get_one(model, pk_id)


	