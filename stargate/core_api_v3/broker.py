from six import with_metaclass
import inspect
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


class ResourceManagerBroker:
    def __init__(self):
        self.created_managers = set()

    def register(self, apimanager):
        self.created_managers.add(apimanager)


class FindModel(with_metaclass(Singleton, ResourceManagerBroker)):

    def __call__(self, resource_type, _apimanager=None, **kw):
        if _apimanager is not None:
            return _apimanager.model_for(resource_type, **kw)
        for manager in self.created_managers:
            try:
                return self(resource_type, _apimanager=manager, **kw)
            except ValueError:
                pass
        message = ('No model with collection name {0} is known to any'
                   ' APIManager objects; maybe you have not set the'
                   ' `collection_name` keyword argument when calling'
                   ' `APIManager.create_api()`?').format(resource_type)
        raise ValueError(message)


class FindCollection(with_metaclass(Singleton, ResourceManagerBroker)):

    def __call__(self, model, _apimanager=None, **kw):
        if _apimanager is not None:
            if model not in _apimanager.registered_apis:
                message = ('APIManager {0} has not created an API for model '
                           ' {1}').format(_apimanager, model)
                raise ValueError(message)
            return _apimanager.collection_name(model, **kw)
        for manager in self.created_managers:
            try:
                return self(model, _apimanager=manager, **kw)
            except ValueError:
                pass
        message = ('Model {0} is not known to any APIManager'
                   ' objects; maybe you have not called'
                   ' APIManager.create_api() for this model.').format(model)
        raise ValueError(message)


class FindUrl(with_metaclass(Singleton, ResourceManagerBroker)):

    def __call__(self, model, resource_id=None, relation_name=None,
                 related_resource_id=None, _apimanager=None,
                 relationship=False, **kw):

        if _apimanager is not None:
            if model not in _apimanager.registered_apis:
                message = ('APIManager {0} has not created an API for model '
                           ' {1}; maybe another APIManager instance'
                           ' did?').format(_apimanager, model)
                raise ValueError(message)
            return _apimanager.url_for(model, resource_id=resource_id,
                                       relation_name=relation_name,
                                       related_resource_id=related_resource_id,
                                       relationship=relationship, **kw)
        for manager in self.created_managers:
            try:
                return self(model, resource_id=resource_id,
                            relation_name=relation_name,
                            related_resource_id=related_resource_id,
                            relationship=relationship, _apimanager=manager,
                            **kw)
            except ValueError:
                pass
        message = ('Model {0} is not known to any APIManager'
                   ' objects; maybe you have not called'
                   ' APIManager.create_api() for this model.').format(model)
        raise ValueError(message)


class FindSerializer(with_metaclass(Singleton, ResourceManagerBroker)):

    def __call__(self, model, _apimanager=None, **kw):
        if _apimanager is not None:
            if model not in _apimanager.registered_apis:
                message = ('APIManager {0} has not created an API for model '
                           ' {1}').format(_apimanager, model)
                raise ValueError(message)
            return _apimanager.serializer_for(model, **kw)
        for manager in self.created_managers:
            try:
                return self(model, _apimanager=manager, **kw)
            except ValueError:
                pass
        message = ('Model {0} is not known to any APIManager'
                   ' objects; maybe you have not called'
                   ' APIManager.create_api() for this model.').format(model)
        raise ValueError(message)


class FindPrimaryKey(with_metaclass(Singleton, ResourceManagerBroker)):

    def __call__(self, instance_or_model, _apimanager=None, **kw):
        if isinstance(instance_or_model, type):
            model = instance_or_model
        else:
            model = instance_or_model.__class__

        if _apimanager is not None:
            managers_to_search = [_apimanager]
        else:
            managers_to_search = self.created_managers
        for manager in managers_to_search:
            if model in manager.registered_apis:
                primary_key = manager.primary_key_for(model, **kw)
                break
        else:
            message = ('Model "{0}" is not known to {1}; maybe you have not'
                       ' called APIManager.create_api() for this model?')
            if _apimanager is not None:
                manager_string = 'APIManager "{0}"'.format(_apimanager)
            else:
                manager_string = 'any APIManager objects'
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
