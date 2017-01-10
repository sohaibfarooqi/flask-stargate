from flask._compat import string_types
import importlib


def perform_imports(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if isinstance(val, string_types):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [perform_imports(item, setting_name) for item in val]
    return val


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """
    try:
        # Nod to tastypie's use of importlib.
        parts = val.split('.')
        module_path, class_name = '.'.join(parts[:-1]), parts[-1]
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except ImportError as exc:
        format = "Could not import '%s' for API setting '%s'. %s."
        msg = format % (val, setting_name, exc)
        raise ImportError(msg)


class APISettings(object):
    def __init__(self, user_config=None):
        self.user_config = user_config or {}

    @property
    def DEFAULT_PARSERS(self):
        default = [
            'core_api.parsers.JSONParser',
            'core_api.parsers.URLEncodedParser',
            'core_api.parsers.MultiPartParser',
            'core_api.parsers.APIURLParser'
        ]
        val = self.user_config.get('DEFAULT_PARSERS', default)
        return perform_imports(val, 'DEFAULT_PARSERS')

    @property
    def DEFAULT_RENDERERS(self):
        default = [
            'core_api.renderers.JSONRenderer',
            'core_api.renderers.HTMLRenderer'
        ]
        val = self.user_config.get('DEFAULT_RENDERERS', default)
        return perform_imports(val, 'DEFAULT_RENDERERS')


default_settings = APISettings()
