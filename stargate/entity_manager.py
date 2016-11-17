from .models import Entity
from .query_utils import QueryUtils

class QueryInterface():

	LIST= 'list'
	INSTANCE = 'instance'
	
	_all_types_ = (LIST, INSTANCE)

	def create_query(model, filters):
		return model.query.filter(filters)
	
	def execute_query(query, type):
				
		if type == QueryInterface.LIST:
			return ListQueryInterface._select_list(query)
		
		elif type == QueryInterface.INSTANCE:
			return InstanceQueryInterface._select_one(query)
		
		else:
			print("Resource Type Not Found")
			return None



class InstanceQueryInterface(QueryInterface):
	
	def _select_one(query):
		return query.first()

class ListQueryInterface(QueryInterface):
	
	def _select_list(query):
		return query.all()

class EntityManager():

	_all_model_classes_ = Entity.__subclasses__()

	_all_methods_ = ('get', 'create', 'update', 'delete')

	def get(model, pk_id = None, **kwargs):

		filters = None

		if model in EntityManager._all_model_classes_:

			if pk_id is not None:
				filters = QueryUtils.get_pk_filter(model, pk_id)

			elif kwargs['filters'] is not None:
				filters = FilterFactory.create_filter(model, kwargs['filters'])

			else: 
				print('Filter not set')

			query = QueryInterface.create_query(model, filters)
			result_set = QueryInterface.execute_query(query, QueryInterface.INSTANCE)
			return result_set

		else:
			return None