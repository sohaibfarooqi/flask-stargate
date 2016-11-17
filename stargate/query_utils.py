from sqlalchemy import and_, or_

class QueryFilters():
	

	def get_pk_filter(model, id):

		if type(id) == list:
			return model.id.in_(id)
		
		elif type(id) == int:
			return model.id == id
		
		else:
			return "No Matching type found"

class Operators(Object):
	pass

class LogicalOperators(Operators):
	
	_operators = {
					"AND": and_,
					"OR": or_

				 }

class ComparisonOperators(Operators):
	_operators = {
					"gt" :  '>',
					"gte": '>=',
					"lte": '<=',
					"lt" :   '<',
					"between" :   'BETWEEN'

				 }

class IdentityOperators(Operators):
	_operators = {
					"in" :  in_,
					"nin":  'not in',
					"eq": '==',
					"neq" :   '!='

				 }

class BooleanOperators(Operators):
	_operators = {
					"eqf" :  '== Falas',
					"eqt": '== True'
				 }
