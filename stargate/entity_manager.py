from .models import Entity
import re
import urllib.parse as urlparse
from sqlalchemy import or_, and_

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
					filtr = list()
					query = model.query
					
					for key in filters:
						
						for split_filter in key.split_result:
							logical_op = query_filters.get_logical_operator(split_filter)

							if logical_op is not None:
								base_filters = split_filter.split(logical_op)
								
								for filter_exp in base_filters:
									
									filter_exp = filter_exp.strip()
									op = query_filters.get_column_operator(filter_exp)
									column, value = filter_exp.split(op)
									filtr.append(query_filters.get_filter_expression(filter_exp, op, model))

								query = query_filters.create_query(query, logical_op, filtr)
							
							else:
							
								split_filter = split_filter.strip()
								op = query_filters.get_column_operator(split_filter)
								filter_expression = query_filters.get_filter_expression(split_filter, op, model)

								query = query_filters.append_query(query, key.operator, filter_expression)	
					print(query)
			else:
				query = model.query.get(pk_id)
				return None

		else:
			return None

class QueryFilters():
	
	REGEX_LOGICAL_GROUPS = r'(\)+\s+\b(and|or)\b\s+\(?)'
	REGEX_LOGICAL_OPERATORS = r'\s+\b(and|or)\b\s+'
	REGEX_COLUMN_OPERATORS = r'\s+(\w+)\s+'


	def __init__(self):
		self.filters = list()
	
	def group_logical_operators(self, query_string_dict):
		
		r = re.compile(self.REGEX_LOGICAL_GROUPS, flags = re.I | re.X)
		iterator = r.finditer(query_string_dict)
		
			
		for match in iterator:
			# print (match.span(),match.group(),match.group(2))
			node = FilterNode()
			node.create_node(	range = match.span(), 
								operator = match.group(2), 
								matched_operator = match.group(),
								level = match.group().count(')'),
								query_string = query_string_dict
							  )
			self.filters.append(node)
		self.filters.sort(key = lambda filter: filter.level, reverse = True)
		return self.filters

	def get_logical_operator(self, str):
		r = re.search(self.REGEX_LOGICAL_OPERATORS, str, flags = re.I)
		if r is not None:
			return r.group().strip()
		else:
			return None

	def get_column_operator(self, exp):
		exp = exp.strip()
		op = re.search(self.REGEX_COLUMN_OPERATORS, exp, flags = re.I).group()
		op = op.replace(' ','')
		return op
							
	def get_filter_expression(self, expression, op, model):
		column, value = expression.split(op)
		#TODO: check if column exist and conform value received in request
		column = column.replace('(','')
		column = column.replace(')','')
		column = column.replace(' ','')
		
		value = value.replace('(','')
		value = value.replace(')','')
		value = value.replace(' ','')

		field = getattr(model, column, None)
		attr = list(filter(
						lambda e: hasattr(field, e % op), 
						['%s','%s_','__%s__']
					  ))[0] % op
		return getattr(field, attr)(value)

	def create_query(self, query, op, filters):
		if op == 'and':
			return query.filter(and_(*filters))

		elif op == 'or':
			return query.filter(or_(*filters))

		else:
			print("No Operator Found %s" %logical_op)

	def append_query (self, query, op, filters):
		if op == 'and':
			return query.filter(and_(filters))

		elif op == 'or':
			return query.filter(or_(filters))

		else:
			print("No Operator Found %s" %logical_op)

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