import cStringIO

from objectcube.factory import get_service_class
from objectcube.exceptions import ObjectCubeDatabaseException

from base import TestDatabaseAwareTest


class TestObjectService(TestDatabaseAwareTest):
    def __init__(self, *args, **kwargs):
        super(TestObjectService, self).__init__(*args, **kwargs)
        self.object_service = get_service_class('ObjectService')

    def test_count_returns_number(self):
        count = self.object_service.count()
        self.assertTrue(isinstance(count, int),
                        msg='The count function should return a list objects')

    def test_count_returns_zero_when_no_object_has_been_added(self):
        count = self.object_service.count()
        self.assertEquals(count,
                          0,
                          msg='When no object has been added, '
                              'count should return zero')

    def test_add_object_returns_int(self):
        stream = cStringIO.StringIO('Hello world')
        stream.seek(0)
        returning_id = self.object_service.add(stream=stream, name='foo.jpg')
        self.assertTrue(
            isinstance(returning_id, int),
            msg='The object add function should return value of type int.')

    def test_add_object_digest_name_uniqueness(self):
        object_name = 'name.txt'

        self.object_service.add(stream=cStringIO.StringIO('stream'),
                                name=object_name)

        with self.assertRaises(ObjectCubeDatabaseException,
                               msg='Adding the same object stream with the'
                                   ' same name will should cause exception'):
            self.object_service.add(stream=cStringIO.StringIO('stream'),
                                    name=object_name)