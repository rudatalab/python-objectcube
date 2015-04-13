import importlib
import logging

from objectcube.services.base.service import Service
from objectcube.settings import FACTORY_CONFIG
from objectcube.exceptions import ObjectCubeException

logger = logging.getLogger('factory')


def load_class(class_path):
    class_data = class_path.split(".")
    module_path = ".".join(class_data[:-1])
    class_str = class_data[-1]

    try:
        module = importlib.import_module(module_path)
        klass = getattr(module, class_str)
        return klass

    except Exception as ex:
        message = 'Unable to fetch class by classpath {0}. Error {1}'\
            .format(class_path, ex.message)
        logger.error(message)
        raise ObjectCubeException(message, ex)


def get_service(service_name, *args, **kwargs):

    # Check if the service_name has been configured in settings
    if service_name not in FACTORY_CONFIG.keys():
        raise ObjectCubeException('Service class {} has not been '
                                  'configured'.format(service_name))

    klass_path = FACTORY_CONFIG.get(service_name)
    klass = load_class(klass_path)

    if not issubclass(klass, Service):
        raise ObjectCubeException('{} is not subclass of Service'
                                  .format(klass_path))

    return klass(*args, **kwargs)