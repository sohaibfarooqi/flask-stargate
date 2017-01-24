from .base_collection import error_response
from .base_collection import SingleKeyError
from .base_collection import BaseAPI
from sqlalchemy.inspection import inspect

class CollectionAPI(BaseAPI):
    
    def __init__(self, *args, **kw):
        super(CollectionAPI, self).__init__(*args, **kw)

        self.changes_on_update = any(column.onupdate is not None for column in inspect(self.model).columns)
    
    def get(self):

        try:
            filters, sort, group_by, single = self._collection_filter_parameters()
        except (TypeError, ValueError, OverflowError) as exception:
            detail = 'Unable to decode filter objects as JSON list'
            return error_response(400, cause=exception, detail=detail)
        except SingleKeyError as exception:
            detail = 'Invalid format for filter[single] query parameter'
            return error_response(400, cause=exception, detail=detail)

        for preprocessor in self.preprocessors['GET_COLLECTION']:
            preprocessor(filters=filters, sort=sort, group_by=group_by,
                         single=single)

        result =  self._get_collection(filters=filters, sort=sort,
                                           group_by=group_by, single=single)
        return result

    