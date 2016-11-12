from .models import Entity
from .query_utils import QueryUtils

class BaseManager():
	
	def initilize_query(Model, filters):
		return Model.query.filter(filters)
	
	def execute_query(query, many = False):
		
		if many:
			return BaseManager._select_list(query)
		else:
			return BaseManager._select_one(query)

	def _select_one(query):
		return query.first()
	
	def _select_list(query):
		return query.all()


class EntityManager(BaseManager):

	_all_model_classes_ = Entity.__subclasses__()

	_all_methods_ = ('get', 'create', 'update', 'delete')

	def get(Model, pk_id = None, **kwargs):

		filters = None

		if Model in EntityManager._all_model_classes_:

			if pk_id is not None:
				filters = QueryUtils.get_pk_filter(Model, pk_id)

			elif kwargs['filters'] is not None:
				filters = FilterFactory.create_filter(Model, kwargs['filters'])

			else: 
				print('Filter not set')

			query = BaseManager.initilize_query(Model, filters)
			result_set = BaseManager.execute_query(query)
			return result_set

		else:
			return None