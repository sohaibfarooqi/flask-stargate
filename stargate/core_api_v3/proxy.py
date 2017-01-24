import inspect
from six import with_metaclass
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.attributes import QueryableAttribute
from sqlalchemy.orm import ColumnProperty

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


class ResourceManagerProxy:
    def __init__(self):
        self.created_managers = set()

    def register(self, resmanager):
        self.created_managers.add(resmanager)


class FindModel(with_metaclass(Singleton, ResourceManagerProxy)):

    def __call__(self, resource_type, _resmanager=None, **kw):
        if _resmanager is not None:
            return _resmanager.model_for(resource_type, **kw)
        for manager in self.created_managers:
            try:
                return self(resource_type, _resmanager=manager, **kw)
            except ValueError:
                pass
        message = ('Collection Name: {0} not registed with ResourceManager. Hence FindModel failed').format(resource_type)
        raise ValueError(message)


class FindCollection(with_metaclass(Singleton, ResourceManagerProxy)):

    def __call__(self, model, _resmanager=None, **kw):
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


class FindUrl(with_metaclass(Singleton, ResourceManagerProxy)):

    def __call__(self, model, resource_id=None, relation_name=None,
                 related_resource_id=None, _resmanager=None,
                 relationship=False, **kw):

        if _resmanager is not None:
            if model not in _resmanager.registered_apis:
                message = ('ResourceManager {0} has not registered API for model {1}').format(_resmanager, model)
                raise ValueError(message)
            return _resmanager.url_for(model, resource_id=resource_id,
                                       relation_name=relation_name,
                                       related_resource_id=related_resource_id,
                                       relationship=relationship, **kw)
        for manager in self.created_managers:
            try:
                return self(model, resource_id=resource_id,
                            relation_name=relation_name,
                            related_resource_id=related_resource_id,
                            relationship=relationship, _resmanager=manager,
                            **kw)
            except ValueError:
                pass
        message = ('Model: {0} is not registered to any ResourceManager object. Hence FindUrl failed').format(model)
        raise ValueError(message)


class FindSerializer(with_metaclass(Singleton, ResourceManagerProxy)):

    def __call__(self, model, _apimanager=None, **kw):
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


class FindPrimaryKey(with_metaclass(Singleton, ResourceManagerProxy)):

    def __call__(self, instance_or_model, _resmanager=None, **kw):
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


url_for = FindUrl()

collection_name = FindCollection()

serializer_for = FindSerializer()

model_for = FindModel()

primary_key_for = FindPrimaryKey()
