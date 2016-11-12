from sqlalchemy import and_, or_

class QueryUtils():
	

	def get_pk_filter(Model, id):
		
		if type(id) == list:
			return Mode.id.in_(id)
		
		elif type(id) == int:
			return Model.id == id
		
		else:
			return "No Matching type found"
