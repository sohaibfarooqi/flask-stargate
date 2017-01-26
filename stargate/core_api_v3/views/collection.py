from .base_collection import BaseAPI
from sqlalchemy.inspection import inspect
from ..exception import StargateException

class CollectionAPI(BaseAPI):
    
    def __init__(self, *args, **kw):
        super(CollectionAPI, self).__init__(*args, **kw)

        self.changes_on_update = any(column.onupdate is not None for column in inspect(self.model).columns)
    
    def get(self):

        try:
            filters, sort, group_by, single = self._collection_filter_parameters()
            # for decorator in self.decorators['GET_COLLECTION']:
            #     decorator(filters=filters, sort=sort, group_by=group_by,
            #              single=single)

            result =  self._get_collection(filters=filters, sort=sort,
                                           group_by=group_by, single=single)
            return result
        except Exception as exception:
            raise StargateException(str(exception))
    