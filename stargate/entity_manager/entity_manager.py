from .models import Entity
import urllib.parse as urlparse
from .query_filter import QueryFilter
import timeit
from functools import partial

class EntityManager():

	def get(model, pk_id, query_string):

		query_embed,query_embed_inner,query_fields = list(), list(), list()
		
		if query_string is not None:

			query_filters, query_order = list(), list()
			offset,page_size = 0,10

			if len(query_string['fields']) > 0:
				fields = query_string['fields']
				query_fields = QueryUtils.get_query_element_list(model, fields, 'fields')

			if len(query_string['embed']) > 0:
				entities = query_string['embed']
				query_embed = QueryUtils.get_query_element_list(model, entities, 'embed')

			if len(query_string['embed_inner']) > 0:
				inner_entities = query_string['embed_inner']
				query_embed_inner = QueryUtils.get_query_element_list(model, inner_entities, 'embed_inner')

			if len(query_string['filters']) > 0:
				print(query_string['filters'])
				query_filters = QueryFilter.create_filters(query_string['filters'], model)

			if len(query_string['sort']) > 0:
				sort_str = query_string['sort']
				query_order = QueryUtils.get_query_element_list(model, sort_str, 'sort')

			if query_string['offset'] > 0:
				offset = query_string['offset']
			
			if query_string['page_size'] > 0:
				page_size = query_string['page_size']

			
			

		if pk_id is None:

			return Entity.get_collection(model, 1, fields = query_fields,
							 						   embed = query_embed,
							 						   embed_inner = query_embed_inner,
												 	   filters = query_filters,
												 	   sort_order = query_order,
												 	   offset = offset,
												 	   page_size = page_size)

		else:
			
			return Entity.get_one(model, pk_id, 1, fields = query_fields,
						 						   embed = query_embed,
						 						   embed_inner = query_embed_inner)


	