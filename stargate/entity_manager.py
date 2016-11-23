from .models import Entity
import re
import urllib.parse as urlparse
from sqlalchemy import or_
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
						pass
						# print(key.operator)
						# print(key.matched_operator)
						# print(key.range)
						# print(key.level)
						# print(key.split_result[0])
						# print(key.split_result[1])
					
					base_filters = filters[0].split_result[0].split('or')
					column, value = base_filters[0].split('eq')
					column1, value1 = base_filters[1].split('gte')

					print(column, value, column1, value1)
					#TODO: check if column exist and conform value received in request
					column = column.replace('(','')
					column = column.replace(')','')
					column = column.replace(' ','')

					column1 = column1.replace('(','')
					column1 = column1.replace(')','')
					column1 = column1.replace(' ','')

					attr = getattr(model, column)
					attr1 = getattr(model, column1)
					query = or_(attr == value, attr1 >= value1)
					print(query)
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
	
	_REGEX_LOGICAL_GROUPS = r'(\)+\s+\b(and|or)\b\s+\(?)'

	def __init__(self):
		self.filters = list()
	
	def group_logical_operators(self, query_string_dict):
		
		r = re.compile(self._REGEX_LOGICAL_GROUPS, flags = re.I | re.X)
		iterator = r.finditer(query_string_dict)
		
			
		for match in iterator:
			# print (match.span(),match.group(),match.group(2))
			node = FilterNode()
			node.create_node(
								range = match.span(), 
								operator = match.group(2), 
								matched_operator = match.group(),
								level = match.group().count(')'),
								query_string = query_string_dict
							  )
			self.filters.append(node)
		self.filters.sort(key = lambda filter: filter.level, reverse = True)
		return self.filters


class FilterNode():
	
	def __init__(self, **kwargs):
		self.range = list()
		self.operator = None
		self.matched_operator = None
		self.level =  None
		self.split_result = None

	def create_node(self, **kwargs):
		self.range = kwargs['range']
		self.operator = kwargs['operator']
		self.matched_operator = kwargs['matched_operator']
		self.level = kwargs['level']
		self.split_result = self._split_filter(self.range, kwargs['query_string'])

	def _split_filter(self, range, query_string):
		init_range = range[0] + 1
		end_range = range[1] - 1
		length = len(query_string)
		return query_string[0:init_range], query_string[end_range:length]