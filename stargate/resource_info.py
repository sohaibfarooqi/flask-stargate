"""Holds information for `models` registered with any `Manager` instance. Can be used within application to 
get information about a resource at runtime. Supported options are primary_key, serializer, deserializer, url, collection_name

"""

import inspect
from six import with_metaclass
from sqlalchemy.orm.attributes import InstrumentedAttribute
from flask import url_for
from .const import ResourceInfoConst

class Singleton(type):
    """Singleton Helper for ResourceInfo.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            supercls = super(Singleton, cls)
            cls._instances[cls] = supercls.__call__(*args, **kwargs)
        return cls._instances[cls]


class RegisteredManagers():
    """Keep a set of all registered :class:`~stargate.manager.Manager` instances.
    """
    def __init__(self):
        self.created_managers = set()

    def register(self, resmanager):
        self.created_managers.add(resmanager)


class ResourceInfo(with_metaclass(Singleton, RegisteredManagers)):
    """This class provides information about a resource registered with any 
    :class:`~stargate.manager.Manager` instance. Data keys include :
        
        - PRIMARY_KEY
        - COLLECTION_NAME
        - URL
        - SERIALIZER
        - DESERIALIZER
    
    This is a Singleton class that can be accessed any where in the application by just
    importing it.

    Example:
    
    .. code-block:: python
    
        from resource_info import resource_info
    
        #returns primary_key for model class User
        resource_info(PRIMARY_KEY, User)

        #returns collection_name for model class User
        resource_info(COLLECTION_NAME, User)

        #returns fully qualified url for model class User
        resource_info(URL, User)

        #returns Serializer class for model class User
        resource_info(SERIALIZER, User)

        #returns DeSerializer class for model class User
        resource_info(DESERIALIZER, User)
    
    Raises `ValueError` if unknown key is provided to the resource_info callable, it also raises 
    `ValueError` if model class is not registered with any :class:`~stargate.manager.Manager` instance.

    """
    def __call__(self, key, instance_or_model, **kw):
        if self.created_managers:
            
            if isinstance(instance_or_model, type):
                model = instance_or_model

            else:
                model = instance_or_model.__class__

            for manager in self.created_managers:

                try:
                    if key == ResourceInfoConst.PRIMARY_KEY:
                        primary_key = manager.registered_apis[model].pk
                        if isinstance(primary_key, str):
                            return primary_key
                        else:
                            return primary_key(model)

                    elif key == ResourceInfoConst.COLLECTION_NAME:
                        return manager.registered_apis[model].collection

                    elif key == ResourceInfoConst.SERIALIZER:
                        return manager.registered_apis[model].serializer

                    elif key == ResourceInfoConst.DESERIALIZER:
                        return manager.registered_apis[model].deserializer

                    elif key == ResourceInfoConst.URL:
                        blueprint_name = manager.registered_apis[model].blueprint
                        api_name = manager.registered_apis[model].apiname
                        parts = [blueprint_name, api_name]
                        url = url_for('.'.join(parts), _external = True, **kw)
                        return url

                    else:
                        raise ValueError("Unknown resource manager attribute: {0}".format(key))
                except ValueError:
                    pass
            message = ('Model: {0} is not registered to any `Manager` instance. Hence Cannot lookup attribute: {1}').format(model, key)
            raise ValueError(message)
        else:
            raise RuntimeError("No Manager Instance Found")

        
#This instance is imported in all other modules.
resource_info = ResourceInfo()