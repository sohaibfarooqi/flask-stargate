from .models import Entity
import re
import urllib.parse as urlparse
# class QueryInterface():

# 	LIST= 'list'
# 	INSTANCE = 'instance'
	
# 	_all_types_ = (LIST, INSTANCE)

# 	def create_query(model, filters):
# 		return model.query.filter(filters)
	
# 	def execute_query(query, type):
				
# 		if type == QueryInterface.LIST:
# 			return ListQueryInterface._select_list(query)
		
# 		elif type == QueryInterface.INSTANCE:
# 			return InstanceQueryInterface._select_one(query)
		
# 		else:
# 			print("Resource Type Not Found")
# 			return None



# class InstanceQueryInterface(QueryInterface):
	
# 	def _select_one(query):
# 		return query.first()

# class ListQueryInterface(QueryInterface):
	
# 	def _select_list(query):
# 		return query.all()

class EntityManager():

	_all_model_classes_ = Entity.__subclasses__()

	_all_methods_ = ('get', 'create', 'update', 'delete')

	def get(model, pk_id, **kwargs):

		if model in EntityManager._all_model_classes_:
			
			if pk_id is None:
				
				if 'filters' in kwargs:
					filter_dict = dict(urlparse.parse_qsl(kwargs['filters'], encoding='utf-8'))
					filter_string = re.sub(r'\s+', '', filter_dict['filters'])
					print(filter_string)
					# filter_string = filter_string.replace('filters','')
					# filter_string = re.sub(r'\s+', '', filter_string)
					# filter_string = filter_string.split('and')
					
					# for filter in filter_string:
					# 	if filter is not None:
					# 		filter = filter.replace('(','')
					# 		filter = filter.replace(')','')
					# 		print('Filter' + filter)

			else:
				filters = FilterFactory.create_filter(model, kwargs['filters'])


			query = QueryInterface.create_query(model, filters)
			result_set = QueryInterface.execute_query(query, QueryInterface.INSTANCE)
			return result_set

		else:
			return None