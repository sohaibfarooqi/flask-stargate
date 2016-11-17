# from sqlalchemy import and_, or_

# class QueryUtils():
	

# 	def create_sql_filter(model, filters):
# 		logical_operators = LogicalOperators.get_operator_list()

# 	def create_sort_order(sort):
# 		pass

# 	def create_pagination(offset,limit):
# 		pass

# class Operators(Object):
	
# 	def get_operator_list(self):
# 		return self._operators.keys()

# 	def get_matching_operator(self, op):
# 		return self._operators[op]

# class LogicalOperators(Operators):
	
# 	_operators = {
# 					"and": and_,
# 					"or" : or_

# 				 }
	
	
# class ComparisonOperators(Operators):
# 	_operators = {
# 					"gt" :  '>',
# 					"gte":  '>=',
# 					"lte":  '<=',
# 					"lt" :  '<',
# 					"between" : 'BETWEEN'

# 				 }

# class IdentityOperators(Operators):
# 	_operators = {
# 					"in" :  in_,
# 					"nin":  'not in',
# 					"eq": '==',
# 					"neq" :   '!='

# 				 }

# class BooleanOperators(Operators):
# 	_operators = {
# 					"eqf" :  '== False',
# 					"eqt":   '== True'
# 				 }
