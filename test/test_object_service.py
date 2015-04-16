
from objectcube.factory import get_service
from objectcube.exceptions import ObjectCubeException
from objectcube.vo import Object, Tagging

from base import ObjectCubeTestCase

from hashlib import md5


def md5_hexdigest(input):
    h = md5()
    h.update(str(input))
    return h.hexdigest()


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

    def create_objects(self, num_objects, name_prefix='object_'):
        objects = []
        for i in range(num_objects):
            objects.append(self.object_service.add(
                Object(
                    digest=md5_hexdigest(i),
                    name='{0}{1}'.format(name_prefix, i)
                )
            ))
        return objects

    def __init__(self, *args, **kwargs):
        super(TestObjectService, self).__init__(*args, **kwargs)
        self.object_service = get_service('ObjectService')
        self.tagging_service = get_service('TaggingService')

    def test_count_returns_number(self):
        count = self.object_service.count()
        self.assertTrue(isinstance(count, (int, long)),
                        msg='The count function should return a list objects')

    def test_count_returns_zero_when_no_object_has_been_added(self):
        self.assert_no_objects_in_data_store()

    def test_count_increases_when_object_is_added(self):
        self.create_objects(num_objects=1)
        self.assert_has_some_objects_in_data_store()
        self.assert_has_number_of_objects_in_data_store(1)

    def test_add_object_raises_exception_if_name_is_missing(self):
        with self.assertRaises(ObjectCubeException):
            self.object_service.add(Object(digest='x', name=None))

        with self.assertRaises(ObjectCubeException):
            self.object_service.add(Object(digest='x', name=''))

    def test_add_object_raises_exception_if_digest_is_missing(self):
        with self.assertRaises(ObjectCubeException):
            self.object_service.add(Object(digest=None, name='x'))

        with self.assertRaises(ObjectCubeException):
            self.object_service.add(Object(digest='', name='x'))

    def test_add_object_returns_object(self):
        in_object = Object(digest=md5_hexdigest('x'), name='foo.jpg')
        db_object = self.object_service.add(in_object)
        self.assertTrue(
            isinstance(db_object, Object),
            msg='The object add function should return value of type Object.')
        self.assertTrue(db_object.id)

    def test_retrieve_by_id(self):
        num_objects = 10
        for i in range(1, num_objects):
            object_name = '{}'.format(i)
            db_object = self.object_service.add(Object(
                digest=md5_hexdigest(object_name),
                name=object_name
            ))
            db_object2 = self.object_service.retrieve_by_id(i)

            self.assertEquals(db_object2.id, db_object.id)
            self.assertEquals(db_object2.name, object_name)
            self.assertEquals(db_object2.digest, db_object.digest)

    def test_retrieve_offset_limit(self):
        number_of_object = 25
        max_fetch = 10
        expected_id_set = set(
            map(lambda o: o.id, self.create_objects(number_of_object)))

        self.assertEquals(number_of_object, len(expected_id_set))

        all_retrieved_set = set()
        offset = 0
        while True:
            objects = self.object_service.retrieve(
                offset=offset, limit=max_fetch)
            retrieved_id_set = set(map(lambda o: o.id, (objects)))
            self.assertTrue(all_retrieved_set.isdisjoint(retrieved_id_set),
                            msg='ids overlap with previously retrieved object'
                            ' when there should be no overlap')
            all_retrieved_set.update(retrieved_id_set)
            if len(objects) != max_fetch:
                self.assertEquals(number_of_object % max_fetch, len(objects))
                break
            offset += max_fetch
        self.assertEquals(expected_id_set, all_retrieved_set)

    def test_fetch_object_outside_offset_return_empty_list(self):
        number_of_object = 20
        self.create_objects(number_of_object)

        objects = self.object_service.retrieve(offset=number_of_object * 10)
        self.assertEquals(len(objects), 0,
                          msg='When selected offset which is outside of the '
                          'data set, then we will get an empty list')

    def test_fetch_object_by_tag(self):
        tag_service = get_service('TagService')
        tag = tag_service.add(self._create_test_tag(value='test-tag-1'))

        test_object = self.create_objects(num_objects=1)[0]
        self.tagging_service.add(test_object, tag, None)
        objects = self.object_service.retrieve_by_tag(tag)

        self.assertEquals(len(objects), 1)
        self.assertEquals(test_object, objects[0])

    def test_fetch_multiple_objects_with_same_tag(self):
        tag_service = get_service('TagService')
        tag = tag_service.add(self._create_test_tag(value='test-tag-1'))

        objects_with_tag = [o for o in self.create_objects(num_objects=10,
                                                           name_prefix='foo')]
        object_not_with_tag = [o for o in
                               self.create_objects(num_objects=10,
                                                   name_prefix='bar')]

        for obj_with_tag in objects_with_tag:
            self.tagging_service.add(obj_with_tag, tag, None)

        _fetched_objects = self.object_service.retrieve_by_tag(tag)

        expected_id_set = set(map(lambda o: o.id, (objects_with_tag)))
        fetched_id_set = set(map(lambda o: o.id, (_fetched_objects)))

        self.assertEqual(expected_id_set, fetched_id_set)

        unexpected_id_set = set(map(lambda o: o.id, (object_not_with_tag)))
        self.assertEqual(
            len(fetched_id_set.intersection(unexpected_id_set)), 0)

    def assert_single_object_with_same_tag(self):
        tag_service = get_service('TagService')
        tag1 = tag_service.add(self.create_test_tag(value='test-tag-1'))
        tag2 = tag_service.add(self.create_test_tag(value='test-tag-2'))

        object_with_tags = self.create_objects(num_objects=1).next()
        self.object_service.add_tags_to_objects(object_with_tags, [tag1, tag2])

        result = self.object_service.retrieve_by_tags(tags=[tag1, tag2])

        self.assertTrue(len(result) == 1,
                        msg='We should only get the object once when he '
                            'has both tags assigned')
