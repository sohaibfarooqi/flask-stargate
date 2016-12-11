import re
from sqlalchemy import or_, and_, desc

class QueryFilter():
	
	REGEX_COLUMN_OPERATORS = r'\s+(\w+)\s+'

	def create_filters(expr_dict, model, validate_fields = 0, validate_values = 0):
		
		sql_filter_set = list()

		try:
			
			for key in expr_dict['priority_filters']:
				
				expr_list = key['expr']
				op = QueryFilter.get_sql_operator(key['op'])
				sql_filter = list()

				for expr in expr_list:
					
					column_operator = QueryFilter.parse_column_operator(expr)
					sql_filter.append(QueryFilter.get_filter_expression(expr.strip(), column_operator, model))
				sql_filter_set.append(op(*sql_filter))
			
			sql_filter = list()
			
			op = QueryFilter.get_sql_operator(expr_dict['simple_filters']['op'])

			for key in expr_dict['simple_filters']['expr']:
				
				column_operator = QueryFilter.parse_column_operator(key)
				sql_filter.append(QueryFilter.get_filter_expression(key.strip(), column_operator, model))	
			
			return (op(*sql_filter_set,*sql_filter))
				

		except KeyError:
			print("Filter type not defined")
			return None

	def get_sql_operator(op):
		
		if op == 'and':
			return and_
		
		elif op == 'or':
			return or_
		
		else:
			return None
	
	def parse_column_operator(exp):
		
		exp = exp.strip()
		op = re.search(QueryFilter.REGEX_COLUMN_OPERATORS, exp, flags = re.I)

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

class QueryFields:

	def get_field_list(str, model):
		
		fields = str.split(',')
		field_list = list()
		
		for field in fields:
			field_list.append(getattr(model, field))
		return field_list

class QueryOrder:

	def get_order_by_list(str, model):

		sort_order_fields = str.split(',')
		sort_order_list = list()
		print(sort_order_fields)

		for key in sort_order_fields:
			
			key = key.strip()

			if key.endswith('-'):

				key = key.replace('-', '')
				field = getattr(model, key)
				sort_order_list.append(field.desc())	
			
			else:
				field = getattr(model, key)
				sort_order_list.append(field)
			
		return sort_order_list
