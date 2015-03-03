import importlib

from objectcube.settings import FACTORY_CONFIG
from objectcube.exceptions import ObjectCubeException


def load_class(class_path):
    class_data = class_path.split(".")
    module_path = ".".join(class_data[:-1])
    class_str = class_data[-1]

    module = importlib.import_module(module_path)
    return getattr(module, class_str)


def get_service(service_name, *args, **kwargs):

    # Check if the service_name has been configured in settings
    if service_name not in FACTORY_CONFIG.keys():
        raise ObjectCubeException('Service class {} has not been '
                                  'configured'.format(service_name))

    class_ = load_class(FACTORY_CONFIG.get(service_name))
    return class_(*args, **kwargs)