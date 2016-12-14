from .models import Entity
import urllib.parse as urlparse
from .query_filter import QueryFilter, QueryUtils
from .parser import Parser

class EntityManager():

	def get(model, pk_id, query_string):

		query_embed,query_embed_inner,query_fields = list(), list(), list()
		
		if query_string is not None:
			
			query_string_dict = urlparse.parse_qs(query_string, encoding = 'utf-8')
			
			query_filters, query_order = list(), list()
			offset,page_size = 0,10

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

			
			

		if pk_id is None:

			return Entity.get_collection(model, 1, fields = query_fields,
							 						   embed = query_embed,
							 						   embed_inner = query_embed_inner,
												 	   filters = query_filters,
												 	   sort_order = query_order,
												 	   offset = offset,
												 	   page_size = page_size 
										)

		else:
			
			return Entity.get_one(model, pk_id, 1, fields = query_fields,
						 						   embed = query_embed,
						 						   embed_inner = query_embed_inner
						 		 )


	