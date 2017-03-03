"""Holds information for `models` registered with any `Manager` instance. Can be used within application to 
get information about a resource at runtime. Supported options are primary_key, serializer, deserializer, url, collection_name

"""

import inspect
from six import with_metaclass
from sqlalchemy.orm.attributes import InstrumentedAttribute
from flask import url_for
from .const import ResourceInfoConst

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

    def __call__(self, key, instance_or_model, **kw):
        if self.created_managers:
            if isinstance(instance_or_model, type):
                model = instance_or_model

            else:
                model = instance_or_model.__class__

            for manager in self.created_managers:

                try:
                    if key == ResourceInfoConst.PRIMARY_KEY_FOR:
                        primary_key = manager.registered_apis[model].pk
                        if isinstance(primary_key, str):
                            return primary_key
                        else:
                            return primary_key(model)

                    elif key == ResourceInfoConst.COLLECTION_NAME_FOR:
                        return manager.registered_apis[model].collection

                    elif key == ResourceInfoConst.SERIALIZER_FOR:
                        return manager.registered_apis[model].serializer

                    elif key == ResourceInfoConst.DESERIALIZER_FOR:
                        return manager.registered_apis[model].deserializer

                    elif key == ResourceInfoConst.URL_FOR:
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

        

manager_info = ManagerInfo()