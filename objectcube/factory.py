import importlib

from objectcube.settings import FACTORY_CONFIG


def load_class(class_path):
    class_data = class_path.split(".")
    module_path = ".".join(class_data[:-1])
    class_str = class_data[-1]

    module = importlib.import_module(module_path)
    return getattr(module, class_str)


def get_service_class(service_name, *args, **kwargs):
    class_ = load_class(FACTORY_CONFIG.get(service_name))
    return class_(*args, **kwargs)