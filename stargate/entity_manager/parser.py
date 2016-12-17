import re
from .exceptions import LogicalOperatorNotFound, ParseException,AmbiguousExpressionException

"""Dated: 13-12-2016
Parsing utility for EntityManager. Defines set of rules to parse filters string received in GET request URL.
"""

class Parser():
	
	"""Contains utility to parse precedence groups, simple filters i.e without grouping. This class assumes to receive
	one kind of boolean logical operator at a certain level. If you wish to use 2 difference operator try enclosing 
	one of them in a precedence group

	Regular Expression:
		- '\((.*?)\)' (Parse precedence groups)
		-  '(((?:(and|or)\s+)*\((%s)\))(?:\s+(and|or))*)' (match groups within query string and identify pre and post logical operators)
		-   '\s+(and|or)\s+' (match logical operator in simple statement)

	Example Filter String: 
		- filters = (name like Milk or name eq mil) and age ge 2 and age ge 2 and (name like Milk or name eq Eggs) and age ge  2
		- filters = (name like Milk or name eq mil) and (name like Milk or name eq Eggs) 
		- filters=name like Milk
	"""

	REGEX_FILTER_GROUPS = r'\((.*?)\)'
	REGEX_EXPRESSION_PARSER = r'(((?:\s+(and|or)\s+)?\((%s)\))(?:\s+(and|or)\s+)?)'
	REGEX_LOGICAL_OPERATORS = r'\s+(and|or)\s+'

	def parse_filters(filter_str):
		
		"""Accepts a string and returns list of filters

		   Args: 
		   	- filter_str (str): Filter string received in request URL.
		   Returns:
		   	- [{},{}], [{},{}]: first list are precedence filters, second list is simple filters   
		"""
		r = re.compile(Parser.REGEX_FILTER_GROUPS)
		iterator = r.finditer(filter_str)
		match_list = list(iterator)
		
		if len(match_list) > 0:
			
			filters, ranges = Parser.parse_priority_group_list(match_list, filter_str)
			priority_filters = list()
			
			for key in Parser.parse_filter_statement_list(filters):
				priority_filters.append(key)
			
			remaining_str, logical_operator = Parser.parse_remaining_filters(filter_str, filters, ranges)
			
			if remaining_str.startswith('(') and remaining_str.endswith(')'):
				remaining_filters_dict = {'expr': None, 'op': logical_operator}
		
			else:	
				remaining_filters,op = Parser.parse_filter_statement(remaining_str)
			
			if op is None and logical_operator is not None:
				op = logical_operator
			
			remaining_filters_dict = {'expr': remaining_filters, 'op': op}
			return priority_filters, remaining_filters_dict
		
		else:
			simple_filters,op = Parser.parse_filter_statement(filter_str)
			return None, {'expr': simple_filters, 'op': op}
	
	def parse_priority_group_list(match_list, query_string):

		"""Parse precedence filters in filter string

		   Args: 
		   	- match_list (str): list of precedence group match against reegx.
		   	- query_string (list): filter string
		   	
		   Returns:
		   	- list, list(tuple(),): first list are actual precedence filters, second is start, end ranges of each filter.
		"""
		filters, group_boundries = list(), list()
		priority_filters, filter_boundaries = zip(*[(match.group(1), match.span()) for match in match_list])
		return priority_filters, filter_boundaries

	def parse_remaining_filters(query_string_dict, filters, group_boundries):
		
		"""Parse simple filters in filter string

		   Args: 
		   	- query_string_dict (str): Filter string received in request URL.
		   	- filters (list): list of precedence filters.
		   	- group_boundries (list of tuples): start-end range of each precedence filters.
		   
		   Returns:
		   	- str, str: first value is str representation of simple filters, second is  logical operator in between   
		"""
		remaining_filters, logical_operator = '', ''
		remaining_str = query_string_dict
		operators = set()

		for count, key in enumerate(filters):
			match_string = list()
			
			match_string = re.search(Parser.REGEX_EXPRESSION_PARSER % key, query_string_dict, flags = re.I).groups()

			expr_with_both_operator = match_string[0]
			expr_with_pre_operator = match_string[1]
			pre_operator = match_string[2]
			post_operator = match_string[4]
			
			if pre_operator is None and post_operator is None:
				raise ParseException(expr_with_both_operator)

			logical_operator = pre_operator
			
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

			if len(operators) > 1:
				raise AmbiguousExpressionException(expr_with_both_operator.strip())

			remaining_str =  remaining_str.replace(string_to_match,'')
		
		
		remaining_str = re.sub(r'\s+', ' ', remaining_str)
		remaining_str = remaining_str.strip()
		return remaining_str, logical_operator
	
	def parse_filter_statement_list(expr):

		"""Parse list of filters to individual statement

		   Args: 
		   	- expr (list): Filters list
		   	
		   Returns:
		   	- list : list of parsed filters, empty in case no filters found   
		"""
		filters_list = list()

		if isinstance(expr, list) or isinstance(expr, tuple):	
			
			for key in expr:
				
				filter,op = Parser.parse_filter_statement(key)
				filters_list.append({'expr': filter, 'op': op})

		return filters_list

	def parse_filter_statement(expr):

		"""Parse individual filter individual statement

		   Args: 
		   	- expr (list): Filters statement
		   	
		   Returns:
		   	- list, str : list of parsed filters, operator in between   
		"""
		operator,base_filters = set(),list()
		operator = set([op for op in Parser.parse_logical_operator(expr)])
		
		if len(operator) > 1:
				raise AmbiguousExpressionException(expr.strip())

		if bool(operator):

			bool_operator = next(iter(operator))
			base_filters = expr.split(bool_operator)
		
		else:

			bool_operator = None
			base_filters.append(expr)
			
		
		return base_filters,bool_operator
		

	def parse_logical_operator(str):

		"""Identify logical boolean operator between filters

		   Args: 
		   	- str (str): Filters statement
		   	
		   Returns:
		   	- list: list of operators found   
		"""
		op_list = list()
		op_list = re.findall(Parser.REGEX_LOGICAL_OPERATORS, str, flags = re.I)

		if not op_list:
			raise LogicalOperatorNotFound(str)
		
		return op_list