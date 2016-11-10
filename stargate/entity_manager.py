from .models import Entity
class BaseManager():

	def _create_query():
		pass
	def _update_query():
		pass
	def _delete_query():
	
class EntityManager(BaseManager):
	_model_classes_ = Entity.__subclass__

	def get(Model, **kwargs):
		
		if Model in _model_classes_:
			
			filters = kwargs['filter'] if kwargs['filter'] else Model.__default_filters__
			sort_order = kwargs['sort_order'] if kwargs['sort_order'] else Model.__default_sort_order__
			offset = kwargs['offset'] if kwargs['offset'] else Model.__default_offset__
			limit= kwargs['limit'] if kwargs['limit'] else Model.__default_limit__

        	result_set = Entity._list(query)
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