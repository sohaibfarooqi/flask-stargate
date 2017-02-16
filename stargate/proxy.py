import inspect
from six import with_metaclass
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.attributes import QueryableAttribute
from sqlalchemy.orm import ColumnProperty

PRIMARY_KEY_FOR = 'primary_key_for'
SERIALIZER_FOR = 'serializer_for'
URL_FOR = 'url_for'
COLLECTION_NAME_FOR = 'collection_name_for'

def primary_key_names(model):
    return [key for key, field in inspect.getmembers(model)
            if isinstance(field, QueryableAttribute)
            and isinstance(field.property, ColumnProperty)
            and field.property.columns[0].primary_key]

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            supercls = super(Singleton, cls)
            cls._instances[cls] = supercls.__call__(*args, **kwargs)
        return cls._instances[cls]


class RegisteredManagers():
    def __init__(self):
        self.created_managers = set()

    def register(self, resmanager):
        self.created_managers.add(resmanager)


class ManagerInfo(with_metaclass(Singleton, RegisteredManagers)):

    def __call__(self, key, model, **kw):
        
        if self.created_managers:
            
            if key == PRIMARY_KEY_FOR:
                self._get_primary_key(primary_resource, kw)
            
            elif key == COLLECTION_NAME_FOR:
                self._get_collection_name(primary_resource, kw)

            elif key == SERIALIZER_FOR:
                self._get_serializer(primary_resource, kw)
            
            elif key == URL_FOR:
                self._get_url(primary_resource, kw)
            else:
                raise ValueError("Unknown resource manager attribute: {0}".format(key))    
        else:
            raise RuntimeError("No Manager Instance registered")

    def _get_collection_name(self, model):
        if _resmanager is not None:
            if model not in _resmanager.registered_apis:
                message = ('ResourceManager {0} has not registered API for model {1}').format(_resmanager, model)
                raise ValueError(message)
            return _resmanager.collection_name(model, **kw)
        for manager in self.created_managers:
            try:
                return self(model, _resmanager = manager, **kw)
            except ValueError:
                pass
        message = ('Model: {0} not registed with ResourceManager. Hence FindCollection failed').format(model)
        raise ValueError(message)

    def _get_url(self, model, pk_id = None, relation = None, related_id = None):

        if _resmanager is not None:
            if model not in _resmanager.registered_apis:
                message = ('ResourceManager {0} has not registered API for model {1}').format(_resmanager, model)
                raise ValueError(message)
            return _resmanager.url_for(model, pk_id = pk_id,
                                       relation = relation,
                                       related_id=related_id,**kw)
        for manager in self.created_managers:
            try:
                return self(model, pk_id=pk_id,
                            relation=relation,
                            related_id=related_id,_resmanager=manager,**kw)
            except ValueError:
                pass
        message = ('Model: {0} is not registered to any ResourceManager object. Hence FindUrl failed').format(model)
        raise ValueError(message)

    def _get_serializer(self, model):
        if _apimanager is not None:
            if model not in _apimanager.registered_apis:
                message = ('ResourceManager {0} has not registered API for model {1}').format(_apimanager, model)
                raise ValueError(message)
            return _apimanager.serializer_for(model, **kw)
        for manager in self.created_managers:
            try:
                return self(model, _apimanager=manager, **kw)
            except ValueError:
                pass
        message = ('Model {0} is not registered to any ResourceManager object. Hence FindSerializer failed').format(model)
        raise ValueError(message)

    def _get_primary_key(self, model):
        if isinstance(instance_or_model, type):
            model = instance_or_model
        else:
            model = instance_or_model.__class__

        if _resmanager is not None:
            managers_to_search = [_resmanager]
        else:
            managers_to_search = self.created_managers
        for manager in managers_to_search:
            if model in manager.registered_apis:
                primary_key = manager.primary_key_for(model, **kw)
                break
        else:
            message = ('ResourceManager {0} has not registered API for model {1}')
            if _resmanager is not None:
                manager_string = 'ResourceManager "{0}"'.format(_resmanager)
            else:
                manager_string = 'any ResourceManager objects'
            message = message.format(model, manager_string)
            raise ValueError(message)

        if primary_key is None:
            pk_names = primary_key_names(model)
            primary_key = 'id' if 'id' in pk_names else pk_names[0]
        return primary_key

manager_info = ManagerInfo()