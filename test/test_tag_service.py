from base import ObjectCubeTestCase
from objectcube.exceptions import ObjectCubeException
from objectcube.vo import Tag, Concept, Plugin

from objectcube.factory import get_service
from random import shuffle
from types import StringType

class TestTagService(ObjectCubeTestCase):

    def __init__(self, *args, **kwargs):
        super(TestTagService, self).__init__(*args, **kwargs)
        self.tag_service = get_service('TagService')
        self.plugin_service = get_service('PluginService')
        self.concept_service = get_service('ConceptService')

    def _create_test_tag(self, id=None,
                         value=None, description=None,
                         mutable=None, type=None,
                         plugin=None, concept=None):
        """
        Helper function for creating test tags in tests.
        :param value: Value for the tag being created
        :return: Tag instance that can be added to data store.
        """
        return Tag(**{
            'id': None if id is None else id,
            'value': '' if value is None else value,
            'description': '' if description is None else description,
            'mutable': False if mutable is None else mutable,
            'type': 0 if type is None else type,
            'concept_id': None if concept is None else concept.id,
            'plugin_id': None if plugin is None else plugin.id,
        })

    def _add_test_tags(self,
                       values, description=None,
                       mutable=None, type=None,
                       plugin=None, concept=None):
        """
        Helper function for creating db tags in tests.
        :param values: Values for the tags to be added.
        :return: Tags added to data store.
        """
        tags = []
        shuffle(values)
        for value in values:
            tag = self._create_test_tag(value=str(value),
                                        description=description,
                                        type=type, mutable=mutable,
                                        plugin=plugin, concept=concept)
            tags.append(self.tag_service.add(tag))
        self.assertEquals(len(values), len(tags))
        return tags

    def _tags_to_id_set(self, tags):
        """
        Helper to create id sets from tag list for testing union, intersect, etc.
        :param tags: List of tags to create id set from
        :return set containing the ids of the input tags
        """
        return set(map(lambda t: t.id, tags))

    def test_tag_count_returns_number(self):
        val = self.tag_service.count()
        self.assertTrue(isinstance(val, (int, long)),
                        msg='The count function should return a integer')

    def test_tag_count_return_zero_when_database_is_empty(self):
        self.assertTrue(self.tag_service.count() == 0,
                        msg='When no tags have been added to data storage, '
                            'then the count function should '
                            'return the value zero.')

    def test_tag_retrieve_returns_list(self):
        self.assertTrue(isinstance(self.tag_service.retrieve(), list),
                        msg='The return value from retrieve should be of '
                            'type list')

    def test_tag_retrieve_returns_empty_list(self):
        tags = self.tag_service.retrieve()
        self.assertTrue(len(tags) == 0,
                        msg='When no tags are in data store then count '
                            'should return empty list')

    def test_tag_retrieve_offset_limit(self):
        number_of_tags = 43
        max_fetch = 10
        expected_id_set = self._tags_to_id_set(
            self._add_test_tags(range(number_of_tags)))
        self.assertEquals(number_of_tags, len(expected_id_set))

        all_retrieved_set = set()
        offset = 0
        while True:
            tags = self.tag_service.retrieve(offset=offset, limit=max_fetch)
            retrieved_id_set = self._tags_to_id_set(tags)
            self.assertTrue(all_retrieved_set.isdisjoint(retrieved_id_set),
                            msg='ids overlap with previously retrieved tags'
                            ' when there should be no overlap')
            all_retrieved_set.update(retrieved_id_set)
            if len(tags) != max_fetch:
                self.assertEquals(number_of_tags % max_fetch, len(tags))
                break
            offset += max_fetch
        self.assertEquals(expected_id_set, all_retrieved_set)

    def test_tag_retrieve_by_id_limit_same_as_count(self):
        number_of_tags = 43
        max_fetch = 43
        expected_id_set = self._tags_to_id_set(
            self._add_test_tags(range(number_of_tags)))
        self.assertEquals(number_of_tags, len(expected_id_set))

        all_retrieved_set = set()
        offset = 0
        while True:
            tags = self.tag_service.retrieve(offset=offset, limit=max_fetch)
            retrieved_id_set = self._tags_to_id_set(tags)
            self.assertTrue(all_retrieved_set.isdisjoint(retrieved_id_set),
                            msg='ids overlap with previously retrieved tags'
                            ' when there should be no overlap')
            all_retrieved_set.update(retrieved_id_set)
            if len(tags) != max_fetch:
                self.assertEquals(number_of_tags % max_fetch, len(tags))
                break
            offset += max_fetch
        self.assertEquals(expected_id_set, all_retrieved_set)

    def test_tag_fetch_tag_outside_offset_return_empty_list(self):
        number_of_tags = 20
        for i in range(number_of_tags):
            self.tag_service.add(self._create_test_tag(value=str(i)))

        tags = self.tag_service.retrieve(offset=100)
        self.assertTrue(len(tags) == 0,
                        msg='When selected offset which is outside of the '
                            'data set, then we will get an empty list')

    def test_tag_add_raises_exception_if_has_id(self):
        t = self._create_test_tag()
        t.id = 12
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(t)

    def test_tag_add_updates_id_field(self):
        t_in = self._create_test_tag()
        t_out = self.tag_service.add(t_in)
        self.assertTrue(t_out.id)
        self.assertTrue(t_out.id > 0)

    def test_tag_add_returns_tag(self):
        test_tag = self._create_test_tag()
        tag = self.tag_service.add(test_tag)
        test_tag.id = tag.id
        self.assertEquals(tag, test_tag)

    def test_tag_add_increases_count(self):
        self.assertEquals(self.tag_service.count(), 0)
        self.tag_service.add(self._create_test_tag())
        self.assertEquals(self.tag_service.count(), 1)

    def test_tag_add_duplicate_increases_count(self):
        self.tag_service.add(self._create_test_tag(value='Bjorn'))
        self.assertEquals(self.tag_service.count(), 1)
        self.tag_service.add(self._create_test_tag(value='Bjorn'))
        self.assertEquals(self.tag_service.count(), 2)

    def test_tag_add_raises_exception_with_illegal_tag_arguments(self):
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add('1')
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add('Bjorn')
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(None)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(1)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(0)

    def test_tag_add_illegal_tag_fails(self):
        number_of_tags = 25
        tags = self._add_test_tags(range(number_of_tags))
        count = self.tag_service.count()

        # Test tags with illegal VALUE
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value=None))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value=True))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value=False))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value=0))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value=1))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value=3.1415297))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value=Tag()))

        # Test tags with illegal TYPE
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=None))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=True))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=False))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type='0'))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type='ID'))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=3.1415297))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=Tag()))

        # Test tags with illegal DESCRIPTION
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=1, description=0))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=1, description=1))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=1, description=True))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=1, description=False))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=1, description=3.1415297))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=1, description=Tag()))

        # Test tags with illegal MUTABLE
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=1, mutable=0))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=1, mutable=1))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=1, mutable='0'))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=1, mutable='BJORN'))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=1, mutable=3.1415297))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=1, mutable=Tag()))

        # Test tags with illegal CONCEPT_ID
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=1, concept_id=True))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=1, concept_id='0'))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=1, concept_id='BJORN'))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=1, concept_id=3.1415297))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=1, concept_id=Tag()))

        # Test with non-existent CONCEPT_ID
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=1, concept_id=0))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=1, concept_id=-12))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=1, concept_id=2000101))

        # Test tags with illegal PLUGIN_ID
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=1, plugin_id=True))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=1, plugin_id='0'))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=1, plugin_id='BJORN'))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=1, plugin_id=3.1415297))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=1, plugin_id=Tag()))

        # Test with non-existent PLUGIN_ID
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=1, plugin_id=0))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=1, plugin_id=-12))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(value="Valid tag", type=1, plugin_id=2000101))

        self.assertEquals(self.tag_service.count(), count, msg='Illegal tag was added')

    def test_tag_retrieve_duplicate_returns_both(self):
        self.assertEquals(self.tag_service.count(), 0)
        self.tag_service.add(self._create_test_tag(value='Bjorn'))
        self.assertEquals(self.tag_service.count(), 1)
        self.tag_service.add(self._create_test_tag(value='Bjorn'))
        self.assertEquals(self.tag_service.count(), 2)
        retrieved = self.tag_service.retrieve_by_value('Bjorn')
        self.assertEquals(len(retrieved), 2)

    def test_tag_retrieve_by_id_raises_exception_with_illegal_id_arguments(self):
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_id('1')

        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_id('Bjorn')

        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_id(None)

    def test_tag_retrieve_by_id_returns_nothing_with_non_existing_id_arguments(self):
        tag = self.tag_service.retrieve_by_id(-1)
        self.assertEquals(tag, None, 'Tag returned where none should exist')

        tag = self.tag_service.retrieve_by_id(0)
        self.assertEquals(tag, None, 'Tag returned where none should exist')

        tag = self.tag_service.retrieve_by_id(10000)
        self.assertEquals(tag, None, 'Tag returned where none should exist')

    def test_tag_retrieve_by_id(self):
        t_in = self._create_test_tag()
        t_out = self.tag_service.add(t_in)
        t_from_db = self.tag_service.retrieve_by_id(t_out.id)
        self.assertEquals(t_from_db, t_out)

    def test_tag_retrieve_by_value(self):
        retrieved_before = self.tag_service.retrieve_by_value('42')
        self.assertEquals(len(retrieved_before), 0)

        added_tags = self._add_test_tags(['41', '42', '42', '43'])
        relevant_tags = filter(lambda t: t.value == '42', added_tags)
        retrieve_after = self.tag_service.retrieve_by_value('42')
        self.assertEquals(len(retrieve_after), 2)
        self.assertEquals(self._tags_to_id_set(relevant_tags),
                          self._tags_to_id_set(retrieve_after))

        low = self.tag_service.retrieve_by_value('42', 0, 1)
        high = self.tag_service.retrieve_by_value('42', 1, 1)
        out_of_range = self.tag_service.retrieve_by_value('42', 2, 1)
        self.assertEquals(self._tags_to_id_set(relevant_tags),
                          self._tags_to_id_set(low) |
                          self._tags_to_id_set(high))
        self.assertEquals(0, len(out_of_range))

    def test_tag_retrieve_by_plugin(self):
        db_plugin = self.plugin_service.add(Plugin(name='test1_plugin',
                                                   module='dummy1_plugin'))
        self._add_test_tags(['41', '42', '42', '43'], plugin=db_plugin)
        no_plugin = self.plugin_service.add(Plugin(name='test2_plugin',
                                                   module='dummy2_plugin'))

        db_plugin_set = self.tag_service.retrieve_by_plugin(db_plugin)
        self.assertEquals(len(db_plugin_set), self.tag_service.count())

        no_plugin_set = self.tag_service.retrieve_by_plugin(no_plugin)
        self.assertEquals(len(no_plugin_set), 0)

    def test_tag_retrieve_by_plugin_raises_on_invalid_arguments(self):
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_plugin(None)

        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_plugin(Plugin())

        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_plugin(Concept(id=1))

    def test_tag_retrieve_by_concept(self):
        db_concept = self.concept_service.add(
            Concept(title='test_concept', description='test concept'))
        db_plugin = self.plugin_service.add(Plugin(name='Plugin', module='Module'))
        db_tags = self._add_test_tags(values=['41', '42', '42', '43'], mutable=True)

        retrieved_before = self.tag_service.retrieve_by_concept(db_concept)
        self.assertEquals(len(retrieved_before), 0)

        # add tag with concept or/and assign concept to some of the tags
        tag_ids_with_concept = set()
        new_tag = self._create_test_tag(value='new_concept_tag', concept=db_concept)
        tag_ids_with_concept.add(self.tag_service.add(new_tag).id)

        db_tags[0].concept_id = db_concept.id
        tag_ids_with_concept.add(self.tag_service.update(db_tags[0]).id)

        # by creating with retrieve_or_create..
        add_or_create_tag = self._create_test_tag(value='non_existing_concept_tag',
                                                  concept=db_concept, plugin=db_plugin)
        tag_ids_with_concept.add(
            self.tag_service.retrieve_or_create(add_or_create_tag).id)

        retrieve_after = self.tag_service.retrieve_by_concept(db_concept)
        self.assertEquals(
            self._tags_to_id_set(retrieve_after), tag_ids_with_concept)

    def test_tag_retrieve_by_concept_raises_on_invalid_arguments(self):
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_concept(None)

        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_concept(Concept())

        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_concept(Plugin(id=1))

    def test_tag_retrieve_by_value_raises_on_invalid_arguments(self):
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_value(None)

        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_value(1)

    def test_tag_retrieve_returns_list(self):
        self.assertTrue(
            isinstance(self.tag_service.retrieve_by_value('23f'), list))

    def test_tag_update(self):
        db_tags = self._add_test_tags(values=['a', 'b', 'c'], mutable=True)

        tag = db_tags[1]
        tag.value = 'd'
        tag.description = 'foobar'

        updated_tag = self.tag_service.update(tag)
        self.assertEquals(updated_tag.value, 'd')
        self.assertEquals(updated_tag, tag)

        db_tags2 = self.tag_service.retrieve()
        db_tags2.sort(lambda a, b: a.id - b.id)
        db_tags.sort(lambda a, b: a.id - b.id)
        self.assertEquals(db_tags, db_tags2)

    def test_tag_update_raises_on_invalid_arguments(self):
        with self.assertRaises(ObjectCubeException):
            self.tag_service.update(None)

        with self.assertRaises(ObjectCubeException):
            self.tag_service.update(Tag())

    def test_tag_update_with_illegal_tag_fails(self):
        number_of_tags = 25
        db_tags = self._add_test_tags(range(number_of_tags))
        update_tag = db_tags.pop(1)

        count = self.tag_service.count()
        db_tags = self.tag_service.retrieve()

        # Test tags with illegal VALUE
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value=None))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value=True))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value=False))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value=0))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value=1))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value=3.1415297))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value=Tag()))

        # Test tags with illegal TYPE
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=None))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=True))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=False))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type='0'))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type='ID'))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=3.1415297))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=Tag()))

        # Test tags with illegal DESCRIPTION
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=1, description=0))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=1, description=1))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=1, description=True))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=1, description=False))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=1, description=3.1415297))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=1, description=Tag()))

        # Test tags with illegal MUTABLE
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=1, mutable=0))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=1, mutable=1))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=1, mutable='0'))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=1, mutable='BJORN'))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=1, mutable=3.1415297))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=1, mutable=Tag()))

        # Test tags with illegal CONCEPT_ID
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=1, concept_id=True))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=1, concept_id='0'))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=1, concept_id='BJORN'))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=1, concept_id=3.1415297))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=1, concept_id=Tag()))

        # Test with non-existent CONCEPT_ID
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=1, concept_id=0))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=1, concept_id=-12))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=1, concept_id=2000101))

        # Test tags with illegal PLUGIN_ID
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=1, plugin_id=True))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=1, plugin_id='0'))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=1, plugin_id='BJORN'))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=1, plugin_id=3.1415297))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=1, plugin_id=Tag()))

        # Test with non-existent PLUGIN_ID
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=1, plugin_id=0))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=1, plugin_id=-12))
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(Tag(id=update_tag.id, value="Valid tag", type=1, plugin_id=2000101))

        self.assertEquals(self.tag_service.count(), count, msg='Illegal tag was added')

        db_tags2 = self.tag_service.retrieve()
        db_tags2.sort(lambda a, b: a.id - b.id)
        db_tags.sort(lambda a, b: a.id - b.id)
        self.assertEquals(db_tags, db_tags2, msg='Able to change some tag')

    def test_tag_delete(self):
        db_tags = self._add_test_tags(['a', 'b', 'c'])

        victim = db_tags.pop(1)
        self.tag_service.delete(victim)

        db_tags2 = self.tag_service.retrieve()
        db_tags2.sort(lambda a, b: a.id - b.id)
        db_tags.sort(lambda a, b: a.id - b.id)
        self.assertEquals(db_tags, db_tags2)

    def test_tag_delete_raises_on_invalid_arguments(self):
        with self.assertRaises(ObjectCubeException):
            self.tag_service.delete(None)

        with self.assertRaises(ObjectCubeException):
            self.tag_service.delete(Tag())

    def test_tag_retrieve_or_create(self):
        db_concept = self.concept_service.add(
            Concept(title='test_concept', description='test concept'))
        db_plugin = self.plugin_service.add(Plugin(name='Plugin', module='Module'))
        db_tags = self._add_test_tags(values=['a', 'b', 'c'], concept=db_concept, plugin=db_plugin)

        tag_c = self._create_test_tag(value='c', concept=db_concept, plugin=db_plugin)
        db_tag_c = self.tag_service.retrieve_or_create(tag_c)
        db_tag_c2 = filter(lambda t: t.value == 'c', db_tags)[0]
        self.assertEquals(db_tag_c, db_tag_c2)

        tag_d = self._create_test_tag(value='d', concept=db_concept, plugin=db_plugin)
        db_tag_d = self.tag_service.retrieve_or_create(tag_d)

        db_tag_d2 = self.tag_service.retrieve_by_id(db_tag_d.id)
        self.assertEquals(db_tag_d, db_tag_d2)

    def test_tag_retrieve_or_create_raises_on_invalid_arguments(self):
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_or_create(None)

        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_or_create(Tag(id=1))

    def test_tag_retrieve_or_create_ambiguous_retrieval(self):
        db_concept = self.concept_service.add(
            Concept(title='test_concept', description='test concept'))
        db_plugin = self.plugin_service.add(Plugin(name='Plugin', module='Module'))
        db_tags = self._add_test_tags(values=['a', 'b', 'b', 'c'], concept=db_concept, plugin=db_plugin)

        tag_b = self._create_test_tag(value='b', concept=db_concept, plugin=db_plugin)
        with self.assertRaises(ObjectCubeException):
            db_tag_b = self.tag_service.retrieve_or_create(tag_b)
