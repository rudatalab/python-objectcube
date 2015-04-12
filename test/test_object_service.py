import cStringIO

from objectcube.factory import get_service
from objectcube.exceptions import (ObjectCubeDatabaseException,
                                   ObjectCubeException)
from objectcube.utils import md5_from_stream
from objectcube.vo import Object

from base import ObjectCubeTestCase


class TestObjectService(ObjectCubeTestCase):

    def assert_no_objects_in_data_store(self):
        self.assertEquals(self.object_service.count(), 0,
                          msg='No objects should be in the data store')

    def assert_has_some_objects_in_data_store(self):
        self.assertTrue(self.object_service.count() > 0,
                        msg='Some objects should be in the data store')

    def assert_has_number_of_objects_in_data_store(self, number):
        self.assertEquals(self.object_service.count(), number,
                          msg='The should be {0} object in '
                              'data store'.format(number))

    def get_test_stream(self, stream_data='stream'):
        stream = cStringIO.StringIO(stream_data)
        stream.seek(0)
        return stream

    def create_objects(self, num_objects, name_prefix='object_'):
        for i in range(num_objects):
            stream = cStringIO.StringIO(str(i))
            yield self.object_service.add(
                stream=stream,
                name='{0}{1}'.format(name_prefix, i))

    def __init__(self, *args, **kwargs):
        super(TestObjectService, self).__init__(*args, **kwargs)
        self.object_service = get_service('ObjectService')
        self.blob_service = get_service('BlobService')

    def tearDown(self):
        self.blob_service.flush()

    def test_count_returns_number(self):
        count = self.object_service.count()
        self.assertTrue(isinstance(count, int),
                        msg='The count function should return a list objects')

    def test_count_returns_zero_when_no_object_has_been_added(self):
        self.assert_no_objects_in_data_store()

    def test_count_increases_when_object_is_added(self):
        self.create_objects(num_objects=1).next()
        self.assert_has_some_objects_in_data_store()
        self.assert_has_number_of_objects_in_data_store(1)

    def test_add_object_raises_exception_if_name_is_missing(self):
        with self.assertRaises(ObjectCubeException):
            self.object_service.add(stream=self.get_test_stream(), name=None)

        with self.assertRaises(ObjectCubeException):
            self.object_service.add(stream=self.get_test_stream(), name='')

    def test_add_object_raises_exception_if_stream_is_broken(self):
        with self.assertRaises(ObjectCubeException):
            self.object_service.add(stream=None,
                                    name='Some name')

    def test_add_object_returns_object(self):
        stream = cStringIO.StringIO('Hello world')
        stream.seek(0)
        value = self.object_service.add(stream=stream, name='foo.jpg')
        self.assertTrue(
            isinstance(value, Object),
            msg='The object add function should return value of type int.')

    def test_add_object_adds_object_to_blob_storage(self):
        o = self.create_objects(num_objects=1).next()
        self.assertTrue(self.blob_service.has_blob(o.digest),
                        msg='When object is added, it should add the blob to '
                            'blob service and the digest should be found')

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
            self.assertTrue(db_object.digest == md5_from_stream(stream))

    def test_get_objects_offset_limit(self):
        number_of_object = 25
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
            self.assertEquals(o.name, str(i + 10))

        objects = self.object_service.get_objects(offset=20, limit=10)
        self.assertEquals(len(objects), 5)

    def test_fetch_object_outside_offset_return_empty_list(self):
        number_of_object = 20
        for i in range(number_of_object):
            object_name = '{}'.format(i)
            stream = cStringIO.StringIO(str(i))
            self.object_service.add(
                stream=stream,
                name=object_name)

        objects = self.object_service.get_objects(offset=number_of_object * 10)
        self.assertTrue(len(objects) == 0,
                        msg='When selected offset which is outside of the '
                            'data set, then we will get an empty list')

    def test_fetch_object_by_tag(self):
        tag_service = get_service('TagService')
        tag = tag_service.add(self._create_test_tag(value='test-tag-1'))

        test_object = self.create_objects(num_objects=1).next()
        self.object_service.add_tags_to_objects(test_object, tag)
        objects = self.object_service.get_objects_by_tags([tag])

        self.assertTrue(len(objects) == 1)
        self.assertEquals(test_object, objects[0])

    def test_fetch_multiple_objects_with_same_tag(self):
        tag_service = get_service('TagService')
        tag = tag_service.add(self._create_test_tag(value='test-tag-1'))

        objects_with_tag = [o for o in self.create_objects(num_objects=100,
                                                           name_prefix='foo')]
        object_not_with_tag = [o for o in
                               self.create_objects(num_objects=100,
                                                   name_prefix='bar')]

        self.object_service.add_tags_to_objects(objects_with_tag, tag)

        _fetched_objects = self.object_service.get_objects_by_tags(tag)

        self.assertListEqual(objects_with_tag, _fetched_objects)

        for x in object_not_with_tag:
            self.assertTrue(x not in _fetched_objects)

    def assert_single_object_with_same_tag(self):
        tag_service = get_service('TagService')
        tag1 = tag_service.add(self.create_test_tag(value='test-tag-1'))
        tag2 = tag_service.add(self.create_test_tag(value='test-tag-2'))

        object_with_tags = self.create_objects(num_objects=1).next()
        self.object_service.add_tags_to_objects(object_with_tags, [tag1, tag2])

        result = self.object_service.get_objects_by_tags(tags=[tag1, tag2])

        self.assertTrue(len(result) == 1,
                        msg='We should only get the object once when he '
                            'has both tags assigned')
