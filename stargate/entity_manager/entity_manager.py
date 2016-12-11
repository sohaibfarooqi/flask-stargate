from .models import Entity
import urllib.parse as urlparse
from .query_filter import QueryFilter
from .parser import Parser

class EntityManager():

	_all_model_classes_ = Entity.__subclasses__()

	_all_methods_ = ('get', 'post', 'put', 'delete')

	def get(model, pk_id, query_string):

		if model in EntityManager._all_model_classes_:
			
			if pk_id is None:
				
				if query_string is None:
					
					#Default collection critera
					return None
				else:
				
					query_string_dict = dict(urlparse.parse_qsl(query_string, encoding = 'utf-8'))
					group_filters, simple_filters = Parser.parse_filters(query_string_dict['filters'])
					query_filters = QueryFilter.create_filters({'priority_filters': group_filters, 'simple_filters': simple_filters}, model)
				
					return Entity.get_collection(model, query_filters)

		else:
			query = model.query.get(pk_id)
			return None



	