from .models import Entity
import re
import urllib.parse as urlparse
from sqlalchemy import or_, and_

class EntityManager():

	_all_model_classes_ = Entity.__subclasses__()

	_all_methods_ = ('get', 'post', 'put', 'delete')

	def get(model, pk_id, query_string):

		if model in EntityManager._all_model_classes_:
			
			if pk_id is None:
				
				if query_string is not None:
					
					query_string_dict = dict(urlparse.parse_qsl(query_string, encoding = 'utf-8'))
					query_filters = QueryFilters()
					
					filters,operator = query_filters.group_logical_operators(query_string_dict['filters'])
					query = model.query
					filtr = list()

					for key in filters:

						logical_op = query_filters.get_logical_operator(key)
						
						split_filter = key.strip()

						if logical_op is None:
							temp = dict()
							temp = {'expr': query_filters.get_filter_expression(split_filter, op, model), 'op': None}
							op = query_filters.get_column_operator(split_filter)
							filtr.append(temp)
						
						else:

							base_filters = split_filter.split(logical_op)
							temp1 = list()
							for filter_exp in base_filters:

								filter_exp = filter_exp.strip()
								op = query_filters.get_column_operator(filter_exp)
								temp1.append(query_filters.get_filter_expression(filter_exp, op, model))
							
							filtr.append({'expr': temp1, 'op': logical_op})	
					query = query.filter((query_filters.get_sql_operator(operator)(*[query_filters.get_sql_operator(filter['op'])(*filter['expr']) for filter in filtr ])))		
					print(query)
			else:
				query = model.query.get(pk_id)
				return None

		else:
			return None

class QueryFilters():
	
	REGEX_LOGICAL_GROUPS = r'(\)+\s+\b(and|or)\b\s+\(?)'
	REGEX_FILTER_GROUPS = r'\((.*?)\)'
	REGEX_LOGICAL_OPERATORS = r'\s+\b(and|or)\b\s+'
	REGEX_COLUMN_OPERATORS = r'\s+(\w+)\s+'
	GROUP_DELIMITER = ')'

	def __init__(self):
		self.filters = list()
		self.op = None
		self.span_array = list()

	def group_logical_operators(self, query_string_dict):
		
		r = re.compile(self.REGEX_FILTER_GROUPS)
		iterator = r.finditer(query_string_dict)
		
		
		group_boundries = list()
		match_filters = ''
		filters, group_boundries = zip(*[(match.group(1), match.span()) for match in iterator])
		remaining_str = query_string_dict
		for key in filters:
			# remaining_str = re.split(r'(?:(and|or)\s+)*(\(%s\))(?:\s+(and|or))*' % key, query_string_dict)
			remaining_str = re.split(r'and|or\s+%s\s+and|or' % key, query_string_dict)
			print(remaining_str)
		

			
		for count, key in enumerate(group_boundries):
			remaining_str = remaining_str[0:key[0]-length] + remaining_str[key[1]-curr_length:len(remaining_str)-1]
			length = group_boundries[count-1][1] - group_boundries[count-1][0] 
			curr_length = group_boundries[count][1] - group_boundries[count][0] 
			# print(remaining_str) 
			# print(length)
			# print(curr_length)
			# print(key[0]-length)
			# print(key[1]-length-curr_length, len(remaining_str))
		remaining_str = remaining_str.lstrip().rstrip()
		# print(remaining_str) 
		# for match in iterator:

		# 	self.filters.append(match.group(1))
		# 	temp = match.span()

		# 	if not span_element:
		# 		span_element.insert(0,temp[1])
			
		# 	else:
		# 		span_element.insert(1, temp[0])

		# 	if len(span_element) == 2:
		# 		self.span_array.append(span_element)
		# 		span_element = list()

		for key in self.span_array:
			op = query_string_dict[key[0]:key[1]].replace(' ','')
			
			if self.op is None:
				self.op = op
			
			else:
				if op != self.op:
					print("Multiple different logical operators found at same level")
		return self.filters, self.op

	def get_sql_operator(self, op):
		
		if op == 'and':
			return and_
		
		elif op == 'or':
			return or_
		
		else:
			return None

		
	def internal_logical_groups(self, expr):
		r = re.compile(self.REGEX_LOGICAL_GROUPS, flags = re.I | re.X)

		for key in expr:
			iterator = r.finditer(key)
			
			for match in iterator:
				print(match)
				node = FilterNode()
				node.create_node(	range = match.span(), 
							operator = match.group(2), 
							matched_operator = match.group(),
							level = match.group().count(self.GROUP_DELIMITER),
							query_string = key
						  )
				self.filters.append(node)
		
				


	def get_logical_operator(self, str):
		r = re.search(self.REGEX_LOGICAL_OPERATORS, str, flags = re.I)
		if r is not None:
			return r.group().strip()
		else:
			return None

	def get_column_operator(self, exp):
		exp = exp.strip()
		op = re.search(self.REGEX_COLUMN_OPERATORS, exp, flags = re.I).group().strip()
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
			print("No Operator Found %s" %op)

	def append_query(self, query, op, filters):

		if op == 'and':
			return query.filter(and_(filters))

		elif op == 'or':
			return query.filter(or_(filters))

		else:
			print("No Operator Found %s" %op)


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