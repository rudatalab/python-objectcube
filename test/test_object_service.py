import cStringIO

from objectcube.factory import get_service_class
from objectcube.exceptions import ObjectCubeDatabaseException
from objectcube.utils import md5_for_file

from base import ObjectCubeTestCase


class TestObjectService(ObjectCubeTestCase):
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

    def test_get_object_by_id(self):
        num_objects = 10
        for i in range(1, num_objects):
            object_name = '{}'.format(i)
            stream = cStringIO.StringIO(str(i))
            self.object_service.add(
                stream=stream,
                name=object_name)
            db_object = self.object_service.get_by_id(i)

            self.assertTrue(db_object.id == i)
            self.assertTrue(db_object.name == str(i))
            self.assertTrue(db_object.digest == md5_for_file(stream))

    def test_get_objects_offset_limit(self):
        number_of_object = 20
        for i in range(number_of_object):
            object_name = '{}'.format(i)
            stream = cStringIO.StringIO(str(i))
            self.object_service.add(
                stream=stream,
                name=object_name)

        objects = self.object_service.get_objects(offset=0, limit=10)
        self.assertTrue(len(objects) == 10)

        for i, o in enumerate(objects):
            self.assertEquals(o.name, str(i))

        objects = self.object_service.get_objects(offset=10, limit=10)

        for i, o in enumerate(objects):
            self.assertEquals(o.name, str(i+10))

    def test_fetch_object_outside_offset_return_empty_list(self):
        number_of_object = 20
        for i in range(number_of_object):
            object_name = '{}'.format(i)
            stream = cStringIO.StringIO(str(i))
            self.object_service.add(
                stream=stream,
                name=object_name)

        objects = self.object_service.get_objects(offset=number_of_object*10)
        self.assertTrue(len(objects) == 0,
                        msg='When selected offset which is outside of the '
                            'data set, then we will get an empty list')

    def test_add_tag_to_object(self):
        tag_service = get_service_class('TagService')
        tag_id = tag_service.add_tag(self.create_test_tag(value='people'))

        object_id = self.object_service.add(
            stream=cStringIO.StringIO('hello world'),
            name='foobar.jpg')
