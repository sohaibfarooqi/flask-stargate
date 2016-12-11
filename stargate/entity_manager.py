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
					group_filters, rest_operator = QueryFilters.group_logical_operators(query_string_dict['filters'],model)

					query = model.query
					
					for key in group_filters:
						query = query.filter((QueryFilters.get_sql_operator(key['op']))(*[(filters) for filters in key['expr']]))
					
					query = query.filter((QueryFilters.get_sql_operator(rest_operator['op'])(*[(filters) for filters in rest_operator['expr']])))	
					print(query)
			else:
				#Default collection critera
				return None

		else:
			query = model.query.get(pk_id)
			return None

class QueryFilters():
	
	REGEX_FILTER_GROUPS = r'\((.*?)\)'
	REGEX_LOGICAL_OPERATORS = r'\s+(and|or)\s+'
	REGEX_COLUMN_OPERATORS = r'\s+(\w+)\s+'
	REGEX_EXPRESSION_PARSER = r'(((?:(and|or)\s+)*\((%s)\))(?:\s+(and|or))*)'
	
	def group_logical_operators(query_string_dict, model):
		
		r = re.compile(QueryFilters.REGEX_FILTER_GROUPS)
		iterator = r.finditer(query_string_dict)
		
		filters, group_boundries, group_filters, operators = list(), list(), list(), set()
		filters, group_boundries = zip(*[(match.group(1), match.span()) for match in iterator])
		
		remaining_str = query_string_dict
		remaining_filters = ''
		
		for count, key in enumerate(filters):
			
			filter_expr,filter_expr_op = QueryFilters.parse_simple_expression(key, model)
			group_filters.append({'expr': filter_expr, 'op': filter_expr_op})
			
			match_string = list()

			match_string = re.search(r'(((?:(and|or)\s+)*\((%s)\))(?:\s+(and|or))*)' % key, query_string_dict).groups()
			
			expr_with_both_operator = match_string[0]
			expr_with_pre_operator = match_string[1]
			pre_operator = match_string[2]
			post_operator = match_string[4]
			
			if group_boundries[count][1] <= len(query_string_dict) and group_boundries[count][0] != 0:
				string_to_match = expr_with_pre_operator
			else:
				string_to_match = expr_with_both_operator
			
			if pre_operator is None:
				print("Group At Start")
			else:
				operators.add(pre_operator)
			
			if post_operator is None:
				print("Group At End")
			else:
				operators.add(post_operator)
			
			remaining_str =  remaining_str.replace(string_to_match,'')

		remaining_str = re.sub(r'\s+', ' ', remaining_str)
		remaining_str = remaining_str.strip()
		remaining_filters,op = QueryFilters.parse_simple_expression(remaining_str,model)
		remaining_filters_dict = {'expr': remaining_filters, 'op': op}
		
		return group_filters, remaining_filters_dict
		

	def get_sql_operator(op):
		
		if op == 'and':
			return and_
		
		elif op == 'or':
			return or_
		
		else:
			return None

	def parse_simple_expression(expr,model):

		operator = set()
		operator = set([op for op in QueryFilters.get_logical_operator(expr)])
		bool_operator = next(iter(operator))
		base_filters = expr.split(bool_operator)
		filters = list()
		
		for filter_exp in base_filters:
			filter_exp = filter_exp.strip()
			op = QueryFilters.get_column_operator(filter_exp)
			filters.append(QueryFilters.get_filter_expression(filter_exp, op, model))
		return filters,bool_operator

	def get_logical_operator(str):
		
		op_list = re.findall(QueryFilters.REGEX_LOGICAL_OPERATORS, str, flags = re.I)

		if op_list:
			return op_list
		
		else:
			return None
			
	def get_column_operator(exp):
		exp = exp.strip()
		op = re.search(QueryFilters.REGEX_COLUMN_OPERATORS, exp, flags = re.I)

		if op is None:
			print("No Opeator Found")
			return None
		
		else:
			return op.group().strip()
							
	def get_filter_expression(expression, op, model):

		column, value = re.split(r'\s%s\s' % op, expression)
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
