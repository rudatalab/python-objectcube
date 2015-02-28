from base import TestDatabaseAwareTest
from objectcube.exceptions import ObjectCubeException
from objectcube.vo import Tag

from objectcube.factory import get_service_class


class TestTagService(TestDatabaseAwareTest):
    def __init__(self, *args, **kwargs):
        super(TestTagService, self).__init__(*args, **kwargs)
        self.tag_service = get_service_class('TagService')

    def _create_test_tag(self, value=''):
        """
        Helper function for creating test tags in tests.
        :param value: Value for the tag being created
        :return: Tag instance that can be added to data store.
        """
        return Tag(**{
            'id': None,
            'value': value,
            'description': '',
            'mutable': False,
            'type': 0,
            'plugin_id': None
        })

    def test_count_returns_number(self):
        val = self.tag_service.count()
        self.assertTrue(isinstance(val, int),
                        msg='The count function should return a list objects')

    def test_count_return_zero_when_database_is_empty(self):
        self.assertTrue(self.tag_service.count() == 0,
                        msg='When now tags have been added to data storage, '
                            'then the count function should '
                            'return the value zero.')

    def test_get_tags_returns_list(self):
        self.assertTrue(isinstance(self.tag_service.get_tags(), list),
                        msg='The return value from get_tags should be of '
                            'type list')

    def test_get_tags_returns_empty_list(self):
        tags = self.tag_service.get_tags()
        self.assertTrue(len(tags) == 0,
                        msg='When no tags are in data store then count '
                            'should return empty list')

    def test_get_tags_offset_limit(self):
        number_of_tags = 20
        for i in range(number_of_tags):
            self.tag_service.add_tag(Tag(**{
                'value': i,
                'type': 10
            }))

        tags = self.tag_service.get_tags(offset=0, limit=10)
        self.assertTrue(len(tags) == 10)

        for i, tag in enumerate(tags):
            self.assertEquals(tag.value, str(i))

        tags = self.tag_service.get_tags(offset=10, limit=10)

        for i, tag in enumerate(tags):
            self.assertEquals(tag.value, str(i+10))

    def test_fetch_tag_outside_offset_return_empty_list(self):
        number_of_tags = 20
        for i in range(number_of_tags):
            self.tag_service.add_tag(Tag(**{
                'value': i,
                'type': 1
            }))

        tags = self.tag_service.get_tags(offset=100)
        self.assertTrue(len(tags) == 0,
                        msg='When selected offset which is outside of the '
                            'data set, then we will get an empty list')

    def test_add_tag_raises_exception_if_has_id(self):
        t = self._create_test_tag()
        t.id = 12
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add_tag(t)

    def test_add_tag_update_id_field(self):
        t = self._create_test_tag()
        self.tag_service.add_tag(t)
        self.assertTrue(t.id)
        self.assertTrue(t.id > 0)

    def test_add_tag_returns_tag(self):
        test_tag = self._create_test_tag()
        tag = self.tag_service.add_tag(test_tag)
        self.assertEquals(tag, test_tag)

    def test_add_increases_count(self):
        self.assertEquals(self.tag_service.count(), 0)
        self.tag_service.add_tag(self._create_test_tag())
        self.assertEquals(self.tag_service.count(), 1)

    def test_get_by_id_raises_exception_with_illegal_id_arguments(self):
        with self.assertRaises(ObjectCubeException):
            self.tag_service.get_by_id('1')

        with self.assertRaises(ObjectCubeException):
            self.tag_service.get_by_id(-1)

        with self.assertRaises(ObjectCubeException):
            self.tag_service.get_by_id(0)

        with self.assertRaises(ObjectCubeException):
            self.tag_service.get_by_id(None)

    def test_get_by_id(self):
        t = self._create_test_tag()
        self.tag_service.add_tag(t)
        t_from_db = self.tag_service.get_by_id(t.id)
        self.assertEquals(t_from_db, t)

    def test_get_by_value_raises_on_invalid_arguments(self):
        with self.assertRaises(ObjectCubeException):
            self.tag_service.get_by_value(None)

        with self.assertRaises(ObjectCubeException):
            self.tag_service.get_by_value('')

    def test_get_by_value_returns_list(self):
        self.assertTrue(isinstance(self.tag_service.get_by_value('23f'), list))

