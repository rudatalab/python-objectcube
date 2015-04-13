import unittest
from objectcube.factory import load_class, get_service
from objectcube.exceptions import ObjectCubeException
from objectcube.services.base.service import Service
from objectcube.settings import FACTORY_CONFIG


class TestClass(object):
    """
    This class is used in below test cases.
    """
    pass


class TestServiceClass(Service):
    """
    This class is used in below test cases.
    """
    pass


class TestFactory(unittest.TestCase):
    def test_load_class_should_return_correct_class_when_exist(self):
        class_path = '{0}.{1}'.format(self.__module__, TestClass.__name__)
        self.assertEqual(load_class(class_path), TestClass)

    def test_load_class_should_raise_when_class_path_is_incorrect(self):
        with self.assertRaises(ObjectCubeException):
            class_path = 'incorrect.class.path.Class'
            load_class(class_path)

    def test_load_class_should_raise_when_class_is_not_found(self):
        with self.assertRaises(ObjectCubeException):
            class_path = '{0}.{1}'.format(self.__module__, 'NoClass')
            load_class(class_path)

    def test_get_service_raises_if_key_not_registered(self):
        with self.assertRaises(ObjectCubeException):
            get_service('NotRegisteredService')

    def test_get_service_raises_if_registered_class_is_not_found(self):
        FACTORY_CONFIG['TestService'] = '{0}.{1}'.format(self.__module__,
                                                         'NoClass')
        with self.assertRaises(ObjectCubeException):
            get_service('TestService')

    def test_get_service_raises_if_base_class_is_not_service(self):
        FACTORY_CONFIG['TestService'] = '{0}.{1}'.format(self.__module__,
                                                         TestClass.__name__)
        with self.assertRaises(ObjectCubeException):
            get_service('TestService')

    def test_get_service_returns_service_if_found(self):
        FACTORY_CONFIG['TestService'] = '{0}.{1}'\
            .format(self.__module__, TestServiceClass.__name__)
        s = get_service('TestService')
        self.assertEqual(type(s), TestServiceClass)