import re

class Parser():
	
	REGEX_FILTER_GROUPS = r'\((.*?)\)'
	REGEX_EXPRESSION_PARSER = r'(((?:(and|or)\s+)*\((%s)\))(?:\s+(and|or))*)'
	REGEX_LOGICAL_OPERATORS = r'\s+(and|or)\s+'

	def parse_filters(query_string_dict):
		
		r = re.compile(Parser.REGEX_FILTER_GROUPS)
		iterator = r.finditer(query_string_dict)
		
		filters, group_boundries, group_filters, operators = list(), list(), list(), set()
		filters, group_boundries = zip(*[(match.group(1), match.span()) for match in iterator])
		
		remaining_str = query_string_dict
		remaining_filters = ''
		
		for count, key in enumerate(filters):
			
			filter_expr,filter_expr_op = Parser.parse_filter_statement(key)
			group_filters.append({'expr': filter_expr, 'op': filter_expr_op})
			
			match_string = list()

			match_string = re.search(Parser.REGEX_EXPRESSION_PARSER % key, query_string_dict, flags = re.I).groups()
			
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
		remaining_filters,op = Parser.parse_filter_statement(remaining_str)
		remaining_filters_dict = {'expr': remaining_filters, 'op': op}
		
		return group_filters, remaining_filters_dict
	
	def parse_filter_statement(expr):

		operator = set()
		operator = set([op for op in Parser.parse_logical_operator(expr)])
		bool_operator = next(iter(operator))
		base_filters = expr.split(bool_operator)
		filters = list()
		return base_filters,bool_operator
		

	def parse_logical_operator(str):
		
		op_list = re.findall(Parser.REGEX_LOGICAL_OPERATORS, str, flags = re.I)

		if op_list:
			return op_list
		
		else:
			return None