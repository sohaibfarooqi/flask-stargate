from .base_collection import error_response
from .base_collection import SingleKeyError
from .base_collection import CollectionAPIBase
from sqlalchemy.inspection import inspect as sqlalchemy_inspect

class CollectionAPI(CollectionAPIBase):
    
    def __init__(self, *args, **kw):
        super(CollectionAPI, self).__init__(*args, **kw)

        self.changes_on_update = any(column.onupdate is not None for column in sqlalchemy_inspect(self.model).columns)
    
    def get(self):

        try:
            filters, sort, group_by, single = self._collection_parameters()
            print(filters)
        except (TypeError, ValueError, OverflowError) as exception:
            detail = 'Unable to decode filter objects as JSON list'
            return error_response(400, cause=exception, detail=detail)
        except SingleKeyError as exception:
            detail = 'Invalid format for filter[single] query parameter'
            return error_response(400, cause=exception, detail=detail)

        for preprocessor in self.preprocessors['GET_COLLECTION']:
            preprocessor(filters=filters, sort=sort, group_by=group_by,
                         single=single)

        return self._get_collection_helper(filters=filters, sort=sort,
                                           group_by=group_by, single=single)

    