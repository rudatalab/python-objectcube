from objectcube.factory import get_service
from objectcube.exceptions import ObjectCubeException
from objectcube.utils import md5_from_value
from objectcube.data_objects import Object, Tag, Tagging
from base import ObjectCubeTestCase
from types import IntType, LongType


class TestObjectService(ObjectCubeTestCase):

    def __init__(self, *args, **kwargs):
        super(TestObjectService, self).__init__(*args, **kwargs)
        self.object_service = get_service('ObjectService')
        self.tagging_service = get_service('TaggingService')

    def _create_test_tag(self, value=u'Value', description=u'Description',
                         plugin=None, concept=None):
        return Tag(**{
            'id': None,
            'value': value,
            'description': description,
            'mutable': False,
            'type': 0L,
            'concept_id': concept.id if concept is not None else None,
            'plugin_id': plugin.id if plugin is not None else None,
        })

    def _create_objects(self, num_objects, name_prefix=u'object_'):
        objects = []
        for i in range(num_objects):
            objects.append(self.object_service.add(
                Object(
                    digest=unicode(md5_from_value(i)),
                    name=u'{0}{1}'.format(name_prefix, i)
                )
            ))
        return objects

    def _objects_to_id_set(self, concepts):
        return set(map(lambda c: c.id, concepts))

    def assert_no_objects_in_data_store(self):
        self.assertEquals(self.object_service.count(), 0,
                          msg='No objects should be in the data store')

    def assert_has_some_objects_in_data_store(self):
        self.assertTrue(self.object_service.count() > 0,
                        msg='Some objects should be in the data store')

    def assert_has_number_of_objects_in_data_store(self, number):
        self.assertEquals(self.object_service.count(), number,
                          msg='There should be {0} object in '
                              'data store'.format(number))

    def test_object_count_returns_number(self):
        count = self.object_service.count()
        self.assertTrue(isinstance(count, (IntType, LongType)),
                        msg='The count function should return a number')

    def test_object_count_returns_zero_when_no_object_has_been_added(self):
        self.assert_no_objects_in_data_store()

    def test_object_count_increases_when_object_is_added(self):
        self._create_objects(num_objects=1)
        self.assert_has_some_objects_in_data_store()
        self.assert_has_number_of_objects_in_data_store(1)

    def test_object_add_object_raises_on_illegal_inputs(self):
        with self.assertRaises(ObjectCubeException):
            self.object_service.add(None)
        with self.assertRaises(ObjectCubeException):
            self.object_service.add('ID')
        with self.assertRaises(ObjectCubeException):
            self.object_service.add(0)
        with self.assertRaises(ObjectCubeException):
            self.object_service.add(1)
        with self.assertRaises(ObjectCubeException):
            self.object_service.add(-1)
        with self.assertRaises(ObjectCubeException):
            self.object_service.add(3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.object_service.add(Object())

        with self.assertRaises(ObjectCubeException):
            self.object_service.add(Object(id=0L,
                                           name=u'Name', digest=u'Desc'))
        with self.assertRaises(ObjectCubeException):
            self.object_service.add(Object(id=1L,
                                           name=u'Name', digest=u'Desc'))
        with self.assertRaises(ObjectCubeException):
            self.object_service.add(Object(id=-1L,
                                           name=u'Name', digest=u'Desc'))
        with self.assertRaises(ObjectCubeException):
            self.object_service.add(Object(id='ID',
                                           name=u'Name', digest=u'Desc'))
        with self.assertRaises(ObjectCubeException):
            self.object_service.add(Object(id=3.1415297,
                                           name=u'Name', digest=u'Desc'))
        with self.assertRaises(ObjectCubeException):
            self.object_service.add(Object(id=Object(),
                                           name=u'Name', digest=u'Desc'))

        with self.assertRaises(ObjectCubeException):
            self.object_service.add(Object(name=0))
        with self.assertRaises(ObjectCubeException):
            self.object_service.add(Object(name=1))
        with self.assertRaises(ObjectCubeException):
            self.object_service.add(Object(name=-1))
        with self.assertRaises(ObjectCubeException):
            self.object_service.add(Object(name=3.1415297))
        with self.assertRaises(ObjectCubeException):
            self.object_service.add(Object(name=Object()))
        with self.assertRaises(ObjectCubeException):
            self.object_service.add(Object(name=''))

        with self.assertRaises(ObjectCubeException):
            self.object_service.add(Object(name='Name', digest=0))
        with self.assertRaises(ObjectCubeException):
            self.object_service.add(Object(name='Name', digest=1))
        with self.assertRaises(ObjectCubeException):
            self.object_service.add(Object(name='Name', digest=-1))
        with self.assertRaises(ObjectCubeException):
            self.object_service.add(Object(name='Name', digest=3.1415297))
        with self.assertRaises(ObjectCubeException):
            self.object_service.add(Object(name='Name', digest=Object()))
        with self.assertRaises(ObjectCubeException):
            self.object_service.add(Object(name='Name', digest=''))

    def test_object_add_object_raises_exception_if_name_is_missing(self):
        with self.assertRaises(ObjectCubeException):
            self.object_service.add(Object(digest='x', name=None))

        with self.assertRaises(ObjectCubeException):
            self.object_service.add(Object(digest='x', name=''))

    def test_object_add_object_raises_exception_if_digest_is_missing(self):
        with self.assertRaises(ObjectCubeException):
            self.object_service.add(Object(digest=None, name=u'x'))

        with self.assertRaises(ObjectCubeException):
            self.object_service.add(Object(digest='', name=u'x'))

    def test_object_add_object_returns_object(self):
        in_object = Object(digest=unicode(md5_from_value(u'x')),
                           name=u'foo.jpg')
        db_object = self.object_service.add(in_object)
        self.assertTrue(
            isinstance(db_object, Object),
            msg='The object add function should return value of type Object.')
        self.assertTrue(db_object.id)

    def test_object_retrieve_by_id_finds_correct_object(self):
        num_objects = 10
        for i in range(1, num_objects):
            object_name = u'{}'.format(i)
            digest = unicode(md5_from_value(object_name))
            object_ = Object(digest=digest, name=object_name)

            db_object = self.object_service.add(object_)
            db_object2 = self.object_service.retrieve_by_id(long(i))

            self.assertEquals(db_object2.id, db_object.id)
            self.assertEquals(db_object2.name, object_name)
            self.assertEquals(db_object2.digest, db_object.digest)

    def test_object_retrieve_by_id_returns_none_on_non_existing_id(self):
        self.assertEquals(self.object_service.retrieve_by_id(23099L), None)

    def test_object_retrieve_by_id_raises_on_invalid_id(self):
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_id(id_=None)
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_id(id_='ID')
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_id(id_=3.141527)
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_id(id_='')
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_id(id_=[])

    def test_object_retrieve_offset_limit(self):
        number_of_object = 25
        max_fetch = 10L
        expected_id_set = set(
            map(lambda o: o.id, self._create_objects(number_of_object)))

        self.assertEquals(number_of_object, len(expected_id_set))

        all_retrieved_set = set()
        offset = 0L
        while True:
            objects = self.object_service.retrieve(
                offset=offset, limit=max_fetch)
            retrieved_id_set = set(map(lambda o: o.id, objects))
            self.assertTrue(all_retrieved_set.isdisjoint(retrieved_id_set),
                            msg='ids overlap with previously retrieved object'
                            ' when there should be no overlap')
            all_retrieved_set.update(retrieved_id_set)
            if len(objects) != max_fetch:
                self.assertEquals(number_of_object % max_fetch, len(objects))
                break
            offset += max_fetch
        self.assertEquals(expected_id_set, all_retrieved_set)

    def test_object_fetch_object_outside_offset_return_empty_list(self):
        number_of_object = 20L
        self._create_objects(number_of_object)

        objects = self.object_service.retrieve(offset=number_of_object * 10)
        self.assertEquals(len(objects), 0,
                          msg='When selected offset which is outside of the '
                          'data set, then we will get an empty list')

    def test_object_retrieve_by_tag_id(self):
        tag_service = get_service('TagService')
        tag = tag_service.add(self._create_test_tag(value=u'test-tag-1'))

        test_object = self._create_objects(num_objects=1)[0]
        tagging = Tagging(tag_id=tag.id, object_id=test_object.id)
        self.tagging_service.add(tagging)

        objects = self.object_service.retrieve_by_tag_id(tag.id)
        self.assertEquals(len(objects), 1)
        self.assertEquals(test_object, objects[0])

    def test_object_retrieve_by_tag_id_multiple_objects_with_same_tag(self):
        tag_service = get_service('TagService')
        tag = tag_service.add(self._create_test_tag(value=u'test-tag-1'))

        objects_with_tag = [ot_ for ot_ in
                            self._create_objects(num_objects=10,
                                                 name_prefix=u'foo')]

        object_not_with_tag = [on_ for on_ in
                               self._create_objects(num_objects=10,
                                                    name_prefix=u'bar')]
        for obj_with_tag in objects_with_tag:
            tagging = Tagging(tag_id=tag.id, object_id=obj_with_tag.id)
            self.tagging_service.add(tagging)

        _fetched_objects = self.object_service.retrieve_by_tag_id(tag.id)

        expected_id_set = set(map(lambda o: o.id, objects_with_tag))
        fetched_id_set = set(map(lambda o: o.id, _fetched_objects))

        self.assertEqual(expected_id_set, fetched_id_set)

        unexpected_id_set = set(map(lambda o: o.id, object_not_with_tag))
        self.assertEqual(
            len(fetched_id_set.intersection(unexpected_id_set)), 0)

    def test_object_retrieve_by_tag_id_zero_objects_with_same_tag(self):
        tag_service = get_service('TagService')
        tag = tag_service.add(self._create_test_tag(value=u'test-tag-1'))
        self._create_objects(num_objects=10, name_prefix=u'bar')

        fetched_objects = self.object_service.retrieve_by_tag_id(tag.id)

        expected_id_set = set()
        fetched_id_set = set(map(lambda o: o.id, fetched_objects))

        self.assertEqual(expected_id_set, fetched_id_set)

    def test_object_delete_raises_if_object_is_not_object(self):
        with self.assertRaises(ObjectCubeException):
            self.object_service.delete('something')

        with self.assertRaises(ObjectCubeException):
            self.object_service.delete(1)

    def test_object_delete_raises_if_object_has_no_id(self):
        with self.assertRaises(ObjectCubeException):
            o = Object(name=u'test.jpg', digest=u'12345')
            self.object_service.delete(o)

    def test_object_delete_raises_if_deleted_object_does_not_exist(self):
        o = Object(name=u'test.jpg', digest=u'12345', id=1337L)
        with self.assertRaises(ObjectCubeException):
            self.object_service.delete(o)

    def test_object_delete_returns_none_if_deleted_object_does_exist(self):
        o = self.object_service.add(Object(name=u'test.jpg', digest=u'12345'))
        delete_return_value = self.object_service.delete(o)
        self.assertEquals(delete_return_value, None)

    def test_object_delete_by_id_raises_on_invalid_id(self):
        with self.assertRaises(ObjectCubeException):
            self.object_service.delete_by_id(id_=None)
        with self.assertRaises(ObjectCubeException):
            self.object_service.delete_by_id(id_='ID')
        with self.assertRaises(ObjectCubeException):
            self.object_service.delete_by_id(id_=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.object_service.delete_by_id(id_=[])

    def test_object_delete_by_id_raises_if_object_does_not_exist(self):
        with self.assertRaises(ObjectCubeException):
            self.object_service.delete_by_id(id_=1234L)

    def test_object_delete_by_id_returns_none_if_object_does_exist(self):
        o = self.object_service.add(Object(name=u'test.jpg', digest=u'12345'))
        delete_return_value = self.object_service.delete_by_id(o.id)
        self.assertEquals(delete_return_value, None)

    def test_object_update_raises_if_not_object(self):
        with self.assertRaises(ObjectCubeException):
            self.object_service.update('test')
        with self.assertRaises(ObjectCubeException):
            self.object_service.update(1)
        with self.assertRaises(ObjectCubeException):
            self.object_service.update(0)
        with self.assertRaises(ObjectCubeException):
            self.object_service.update([])
        with self.assertRaises(ObjectCubeException):
            self.object_service.update(None)

    def test_object_update_raises_if_object_with_no_id(self):
        with self.assertRaises(ObjectCubeException):
            o = Object(name=u'test.jpg', digest=u'12345')
            self.object_service.update(o)

    def test_object_update_raises_if_update_object_that_does_not_exist(self):
        with self.assertRaises(ObjectCubeException):
            o = Object(name=u'test.jpg', digest=u'12345', id=234L)
            self.object_service.update(o)

    def test_object_update_raises_on_illegal_name_digest(self):
        o = self.object_service.add(Object(name=u'name', digest=u'digest'))

        with self.assertRaises(ObjectCubeException):
            self.object_service.update(Object(id=o.id,
                                              name=o.name, digest=None))
        with self.assertRaises(ObjectCubeException):
            self.object_service.update(Object(id=o.id,
                                              name=o.name, digest=''))
        with self.assertRaises(ObjectCubeException):
            self.object_service.update(Object(id=o.id,
                                              name=o.name, digest=0))
        with self.assertRaises(ObjectCubeException):
            self.object_service.update(Object(id=o.id,
                                              name=o.name, digest=1))
        with self.assertRaises(ObjectCubeException):
            self.object_service.update(Object(id=o.id,
                                              name=o.name, digest=-1))
        with self.assertRaises(ObjectCubeException):
            self.object_service.update(Object(id=o.id,
                                              name=o.name, digest=3.1415297))
        with self.assertRaises(ObjectCubeException):
            self.object_service.update(Object(id=o.id,
                                              name=o.name, digest=Object()))

        with self.assertRaises(ObjectCubeException):
            self.object_service.update(Object(id=o.id,
                                              digest=o.name, name=None))
        with self.assertRaises(ObjectCubeException):
            self.object_service.update(Object(id=o.id,
                                              digest=o.name, name=''))
        with self.assertRaises(ObjectCubeException):
            self.object_service.update(Object(id=o.id,
                                              digest=o.name, name=0))
        with self.assertRaises(ObjectCubeException):
            self.object_service.update(Object(id=o.id,
                                              digest=o.name, name=1))
        with self.assertRaises(ObjectCubeException):
            self.object_service.update(Object(id=o.id,
                                              digest=o.name, name=-1))
        with self.assertRaises(ObjectCubeException):
            self.object_service.update(Object(id=o.id,
                                              digest=o.name, name=3.1415297))
        with self.assertRaises(ObjectCubeException):
            self.object_service.update(Object(id=o.id,
                                              digest=o.name, name=Object()))

    def test_object_adding_duplicate_fails(self):
        name1 = u'test-title'
        name2 = u'updated-title'

        digest1 = u'test-digest'
        digest2 = u'updated-digest'

        o1 = self.object_service.add(Object(name=name1, digest=digest1))
        self.assertEqual(o1.name, name1)
        self.assertEqual(o1.digest, digest1)
        o1 = self.object_service.retrieve_by_id(o1.id)
        self.assertEqual(o1.name, name1)
        self.assertEqual(o1.digest, digest1)

        # Changing only digest is OK
        o2 = self.object_service.add(Object(name=name1, digest=digest2))
        self.assertEqual(o2.name, name1)
        self.assertEqual(o2.digest, digest2)
        o2 = self.object_service.retrieve_by_id(o2.id)
        self.assertEqual(o2.name, name1)
        self.assertEqual(o2.digest, digest2)

        # Changing only name is OK
        o3 = self.object_service.add(Object(name=name2, digest=digest1))
        self.assertEqual(o3.name, name2)
        self.assertEqual(o3.digest, digest1)
        o3 = self.object_service.retrieve_by_id(o3.id)
        self.assertEqual(o3.name, name2)
        self.assertEqual(o3.digest, digest1)

        # Changing neither is not OK
        with self.assertRaises(ObjectCubeException):
            self.object_service.add(Object(name=name1, digest=digest1))

    def test_object_update_updates_object(self):
        name1 = u'test-title'
        name2 = u'updated-title'

        digest1 = u'test-digest'
        digest2 = u'updated-digest'

        o1 = self.object_service.add(Object(name=name1, digest=digest1))

        o1.name = name2
        o2 = self.object_service.update(o1)
        self.assertEqual(o2.name, name2)
        self.assertEqual(o2.digest, digest1)

        o2 = self.object_service.retrieve_by_id(o1.id)
        self.assertEqual(o2.name, name2)
        self.assertEqual(o2.digest, digest1)

        o2.digest = digest2
        o3 = self.object_service.update(o2)
        self.assertEqual(o3.name, name2)
        self.assertEqual(o3.digest, digest2)

        o3 = self.object_service.retrieve_by_id(o2.id)
        self.assertEqual(o3.name, name2)
        self.assertEqual(o3.digest, digest2)

        o3.name = name1
        o3.digest = digest1
        o4 = self.object_service.update(o3)
        self.assertEqual(o4.name, name1)
        self.assertEqual(o4.digest, digest1)

        o4 = self.object_service.retrieve_by_id(o3.id)
        self.assertEqual(o4.name, name1)
        self.assertEqual(o4.digest, digest1)

    def test_object_retrieve_raises_on_invalid_limit_offset(self):
        self.assertEquals(0, self.object_service.count(),
                          msg='Database is not empty in beginning')
        self.object_service.add(Object(name=u'Concept', digest=u'Desc'))

        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve(offset=-1L)
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve(offset='0')
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve(offset='ID')
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve(offset=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve(offset=Object(id=0))

        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve(limit=-1L)
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve(limit='0')
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve(limit='ID')
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve(limit=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve(limit=Object(id=0))

    def test_object_retrieve_by_regex_raises_on_invalid_limit_offset(self):
        self.assertEquals(0, self.object_service.count(),
                          msg='Database is not empty in beginning')
        self.object_service.add(Object(name=u'Concept', digest=u'Desc'))

        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_regex(name=u'Test',
                                                  offset=-1L)
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_regex(name=u'Test',
                                                  offset=u'0')
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_regex(name=u'Test',
                                                  offset=u'ID')
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_regex(name=u'Test',
                                                  offset=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_regex(name=u'Test',
                                                  offset=Object(id=0))

        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_regex(name=u'Test',
                                                  limit=-1)
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_regex(name=u'Test',
                                                  limit=u'0')
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_regex(name=u'Test',
                                                  limit=u'ID')
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_regex(name=u'Test',
                                                  limit=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_regex(name=u'Test',
                                                  limit=Object(id=0))

    def test_object_retrieve_by_tag_id_raises_on_invalid_limit_offset(self):
        self.assertEquals(0, self.object_service.count(),
                          msg='Database is not empty in beginning')
        self.object_service.add(Object(name=u'Concept', digest=u'Desc'))

        tag_id = 1L

        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_tag_id(tag_id,
                                                   offset=-1)
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_tag_id(tag_id,
                                                   offset='0')
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_tag_id(tag_id,
                                                   offset='ID')
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_tag_id(tag_id,
                                                   offset=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_tag_id(tag_id,
                                                   offset=Object(id=0))

        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_tag_id(tag_id,
                                                   limit=-1)
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_tag_id(tag_id,
                                                   limit='0')
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_tag_id(tag_id,
                                                   limit='ID')
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_tag_id(tag_id,
                                                   limit=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_tag_id(tag_id,
                                                   limit=Object(id=0))

    def test_object_retrieve_by_regex_raises_on_invalid_name(self):
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_regex(name=0)
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_regex(name=1)
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_regex(name=-1)
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_regex(name=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_regex(name=Object())

    def test_concept_retrieve_by_regex_offset_limit(self):
        number_of_object = 27
        max_fetch = 9L
        concepts = []
        db_objects = self._create_objects(number_of_object)
        expected_id_set = set(map(lambda o: o.id, db_objects))
        self.assertEquals(number_of_object, len(expected_id_set))

        offset = 0L
        all_retrieved_set = set()
        while True:
            objects = self.object_service.retrieve_by_regex(name=u'object*',
                                                            offset=offset,
                                                            limit=max_fetch)
            retrieved_id_set = set(map(lambda o: o.id, objects))
            self.assertTrue(all_retrieved_set.isdisjoint(retrieved_id_set),
                            msg='ids overlap with previously retrieved object'
                            ' when there should be no overlap')
            all_retrieved_set.update(retrieved_id_set)
            if len(objects) != max_fetch:
                self.assertEquals(number_of_object % max_fetch, len(objects))
                break
            offset += max_fetch
        self.assertEquals(expected_id_set, all_retrieved_set)

        offset = 0L
        while True:
            concepts = self.object_service.retrieve_by_regex(
                name=db_objects[0].name,
                offset=offset, limit=max_fetch
            )

            if len(concepts) != max_fetch:
                break
            offset += max_fetch
        self.assertEquals(len(concepts), 1,
                          'Returned too many concepts-name should be unique')

        offset = 0L
        while True:
            concepts = self.object_service.retrieve_by_regex(
                name=u'Unknown name',
                offset=offset, limit=max_fetch
            )

            if len(concepts) != max_fetch:
                break
            offset += max_fetch
        self.assertEquals(len(concepts), 0,
                          'Returned too many concepts-name should not exist')

    def test_object_retrieve_by_tag_id_raises_with_illegal_tag_arguments(self):
        tag = self._create_test_tag(value=u'Test title',
                                    description=u'Description')
        tag.id = 1L

        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_tag_id('1')
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_tag_id('Bjorn')
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_tag_id(None)
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_tag_id(1)
        with self.assertRaises(ObjectCubeException):
            self.object_service.retrieve_by_tag_id(0)

        with self.assertRaises(ObjectCubeException):
            tag.id = None
            self.object_service.retrieve_by_tag_id(tag)
        with self.assertRaises(ObjectCubeException):
            tag.id = 'ID'
            self.object_service.retrieve_by_tag_id(tag)
        with self.assertRaises(ObjectCubeException):
            tag.id = 3.1415297
            self.object_service.retrieve_by_tag_id(tag)
        with self.assertRaises(ObjectCubeException):
            tag.id = []
            self.object_service.retrieve_by_tag_id(tag)

    def test_update_updates_object_name(self):
        before_change_title = u'test-title'
        after_change_title = u'updated-title'
        o1 = self.object_service.add(Object(name=before_change_title,
                                            digest=u'12345'))

        o1.name = after_change_title
        o2 = self.object_service.update(o1)
        self.assertEquals(o2.name, after_change_title)

        o3 = self.object_service.retrieve_by_id(o1.id)
        self.assertEquals(o3.name, after_change_title)
