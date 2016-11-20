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

	def get(model, pk_id, query_string):

		if model in EntityManager._all_model_classes_:
			
			if pk_id is None:
				
				if query_string is not None:
					
					query_string_dict = dict(urlparse.parse_qsl(query_string, encoding = 'utf-8'))
					query_filters = QueryFilters()
					filters = query_filters.group_logical_operators(query_string_dict['filters'])
					
					for key in filters:
						print(key.operator)
						print(key.matched_operator)
						print(key.range)
						print(key.level)
						print(key.split_result)
					# print(query_string_dict)
					# filter_string = re.sub(r'\s+', '', query_string_dict['filters'])
					
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


			# query = QueryInterface.create_query(model, filters)
			# result_set = QueryInterface.execute_query(query, QueryInterface.INSTANCE)
			# return result_set
			return None

		else:
			return None

class QueryFilters():
	
	def __init__(self):
		self.filters = list()
	
	def group_logical_operators(self, query_string_dict):
		
		r = re.compile(r'(\)+\s+\b(and|or)\b\s+\(+)', flags = re.I | re.X)
		iterator = r.finditer(query_string_dict)
		
			
		for match in iterator:
			print (match.span(),match.group(),match.group(2))
			span = match.span()
			print(span[0], span[1])
			node = FilterNode(
								range = match.span(), 
								operator = match.group(2), 
								matched_operator = match.group(),
								level = match.group().count(')'),
								split_result = query_string_dict[span[0]:span[1]]

							  )
			self.filters.append(node)
		self.filters.sort(key = lambda filter: filter.level, reverse = True)
		return self.filters


class FilterNode():
	
	range = []
	operator = None
	matched_operator = None
	level =  None
	split_result = None

	def __init__(self, **kwargs):
		self.__dict__.update(kwargs)
		for key in kwargs:
			self.key = kwargs[key]