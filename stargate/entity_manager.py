from .models import Entity
class BaseManager():

	def _create_query():
		pass
	def _update_query():
		pass
	def _delete_query():
		pass
	def _select_query():
		pass


class EntityManager(BaseManager):
	
	_all_model_classes_ = Entity.__subclass__
	
	_all_methods = ('get', 'create', 'update', 'delete')

	def get(Model, pk_id = None, **kwargs):
		
		filters,sort_order,fields,offset,limit = None

		if Model in _model_classes_:
			
			if pk_id is None and kwargs['filters'] is None:
				pass
			else:
				filters = FilterFactory.create_filter(Model, pk_id, kwargs['filters'])
			sort_order = kwargs['sort_order'] if kwargs['sort_order'] else Model.__default_sort_order__
			fields = kwargs['fields'] if kwargs['fields'] else Model.__default_fields__
			offset = kwargs['offset'] if kwargs['offset'] else Model.__default_offset__
			limit= kwargs['limit'] if kwargs['limit'] else Model.__default_limit__
			
			query = BaseManager.initilize_query(filters, sort_order, offset, limit)
			result_set = BaseManager.execute_query(query)
        	
        	return result_set
       
        else:
        	return None

    def create(Model, filters = None):
        result = Model.query.get(filters)
        return result

    def update(data):
        db.session.add(data)
        db.session.commit
        return data.id
   
    def delete(Model,id):
        return  Model.query.filter(Model.id == id).delete()