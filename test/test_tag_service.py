from base import ObjectCubeTestCase
from objectcube.exceptions import ObjectCubeException
from objectcube.data_objects import Tag, Concept, Plugin
from objectcube.factory import get_service
from random import shuffle


class TestTagService(ObjectCubeTestCase):

    def __init__(self, *args, **kwargs):
        super(TestTagService, self).__init__(*args, **kwargs)
        self.tag_service = get_service('TagService')
        self.plugin_service = get_service('PluginService')
        self.concept_service = get_service('ConceptService')

    def _create_test_tag(self, id_=None,
                         value=None, description=None,
                         mutable=None, type_=None,
                         plugin=None, concept=None):
        """
        Helper function for creating test tags in tests.
        :param value: Value for the tag being created
        :return: Tag instance that can be added to data store.
        """
        if description is None and value is not None:
            description = u'Desc_' + value
        return Tag(**{
            'id': None if id_ is None else id_,
            'value': u'V' if value is None else value,
            'description': u'Desc' if description is None else description,
            'mutable': False if mutable is None else mutable,
            'type': 1L if type_ is None else type_,
            'concept_id': None if concept is None else concept.id,
            'plugin_id': None if plugin is None else plugin.id,
        })

    def _add_test_tags(self,
                       values, description=None,
                       mutable=None, type_=None,
                       plugin=None, concept=None):
        """
        Helper function for creating db tags in tests.
        :param values: Values for the tags to be added.
        :return: Tags added to data store.
        """
        tags = []
        shuffle(values)
        for value in values:
            tag = self._create_test_tag(value=u'Tag_'+unicode(value),
                                        description=description,
                                        type_=type_, mutable=mutable,
                                        plugin=plugin, concept=concept)
            tags.append(self.tag_service.add(tag))
        self.assertEquals(len(values), len(tags))
        return tags

    def _tags_to_id_set(self, tags):
        """
        Helper to create id sets from tag list for testing union, etc.
        :param tags: List of tags to create id set from
        :return set containing the ids of the input tags
        """
        return set(map(lambda t: t.id, tags))

    # ==== count()

    def test_tag_count_returns_number(self):
        val = self.tag_service.count()
        self.assertTrue(isinstance(val, (int, long)),
                        msg=u'The count function should return a integer')

    def test_tag_count_return_zero_when_database_is_empty(self):
        self.assertTrue(self.tag_service.count() == 0,
                        msg=u'When no tags have been added to data storage, '
                            u'count should return zero.')

    # ==== add()

    def test_tag_add_returns_tag(self):
        test_tag = self._create_test_tag()
        tag = self.tag_service.add(test_tag)
        test_tag.id = tag.id
        self.assertEquals(tag, test_tag)

    def test_tag_add_increases_count(self):
        self.assertEquals(self.tag_service.count(), 0)
        self.tag_service.add(self._create_test_tag())
        self.assertEquals(self.tag_service.count(), 1)

    def test_tag_add_updates_id_field(self):
        t_in = self._create_test_tag()
        t_out = self.tag_service.add(t_in)
        self.assertTrue(t_out.id)
        self.assertTrue(t_out.id > 0)

    def test_tag_add_raises_exception_if_has_id(self):
        t = self._create_test_tag()
        t.id = 12L
        with self.assertRaises(ObjectCubeException):
            self.tag_service.add(t)

    def test_tag_add_duplicate_increases_count(self):
        self.tag_service.add(self._create_test_tag(value=u'Bjorn'))
        self.assertEquals(self.tag_service.count(), 1)
        self.tag_service.add(self._create_test_tag(value=u'Bjorn'))
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
        self._add_test_tags(range(number_of_tags))
        count = self.tag_service.count()

        # Test tags with illegal VALUE
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.value = None
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.value = True
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.value = False
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.value = 0
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.value = 1L
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.value = 3.1415297
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.value = []
            self.tag_service.add(tag)

        # Test tags with illegal TYPE
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.type = None
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.type = True
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.type = False
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.type = 0
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.type = u'X'
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.type = 3.1415297
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.type = []
            self.tag_service.add(tag)

        # Test tags with illegal DESCRIPTION
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.description = None
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.description = True
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.description = False
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.description = 0
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.description = 1L
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.description = u''
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.description = 3.1415297
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.description = []
            self.tag_service.add(tag)

        # Test tags with illegal MUTABLE
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.mutable = None
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.mutable = 'XYZ'
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.mutable = u'X'
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.mutable = 0
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.mutable = 1L
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.mutable = u''
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.mutable = 3.1415297
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.mutable = []
            self.tag_service.add(tag)

        # Test tags with illegal CONCEPT_ID
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.concept_id = True
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.concept_id = 'XYZ'
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.concept_id = u'X'
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.concept_id = 0
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.concept_id = False
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.concept_id = u''
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.concept_id = 3.1415297
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.concept_id = []
            self.tag_service.add(tag)

        # Test with non-existent CONCEPT_ID
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.concept_id = 0L
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.concept_id = 2000L
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.concept_id = -1L
            self.tag_service.add(tag)

        # Test tags with illegal PLUGIN_ID
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.plugin_id = True
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.plugin_id = 'XYZ'
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.plugin_id = u'X'
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.plugin_id = 0
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.plugin_id = False
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.plugin_id = u''
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.plugin_id = 3.1415297
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.plugin_id = []
            self.tag_service.add(tag)

        # Test with non-existent PLUGIN_ID
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.plugin_id = 0L
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.plugin_id = 2000L
            self.tag_service.add(tag)
        with self.assertRaises(ObjectCubeException):
            tag = self._create_test_tag()
            tag.plugin_id = -1L
            self.tag_service.add(tag)

        self.assertEquals(self.tag_service.count(), count,
                          msg=u'Illegal tag was added')

    # ==== retrieve_or_create()

    def test_tag_retrieve_or_create(self):
        # Create a database with three tags: a, b, c
        concept1 = Concept(title=u'test_concept1', description=u'test concept')
        concept2 = Concept(title=u'test_concept2', description=u'test concept')
        plugin1 = Plugin(name=u'Plugin1', module=u'Module1')
        plugin2 = Plugin(name=u'Plugin2', module=u'Module2')
        db_concept1 = self.concept_service.add(concept1)
        db_concept2 = self.concept_service.add(concept2)
        db_plugin1 = self.plugin_service.add(plugin1)
        db_plugin2 = self.plugin_service.add(plugin2)
        db_tags = self._add_test_tags(values=[u'a', u'b', u'c'],
                                      concept=db_concept1,
                                      plugin=db_plugin1)
        ids = self._tags_to_id_set(db_tags)

        # Make a copy of one of the tags, remove the ID
        # then see if the original is returned
        tag = self._create_test_tag(value=db_tags[0].value,
                                    concept=db_concept1,
                                    plugin=db_plugin1)
        db_tag = self.tag_service.retrieve_or_create(tag)
        self.assertEquals(db_tag, db_tags[0])

        # Make a copy, change value and make sure it is a new tag
        tag = db_tags[1]
        tag.id = None
        tag.value = u'd'
        db_tag = self.tag_service.retrieve_or_create(tag)
        self.assertNotIn(db_tag.id, ids)
        self.assertNotEqual(db_tag, db_tags[1])

        # Make a copy, change plugin_id and make sure it is a new tag
        tag = db_tags[1]
        tag.id = None
        tag.plugin_id = db_plugin2.id
        db_tag = self.tag_service.retrieve_or_create(tag)
        self.assertNotIn(db_tag.id, ids)
        self.assertNotEqual(db_tag, db_tags[1])

        # Make a copy, change concept_id and make sure it is a new tag
        tag = db_tags[1]
        tag.id = None
        tag.concept_id = db_concept2.id
        db_tag = self.tag_service.retrieve_or_create(tag)
        self.assertNotIn(db_tag.id, ids)
        self.assertNotEqual(db_tag, db_tags[1])

        # Make a copy, change type and make sure it is a new tag
        tag = db_tags[1]
        tag.id = None
        tag.type = 2L
        self.assertNotIn(db_tag.id, ids)
        self.assertNotEqual(db_tag, db_tags[1])

        # Make a new tag, change value and make sure it is a new tag
        tag = self._create_test_tag(value=u'e', description=u'd',
                                    plugin=db_plugin2,
                                    concept=db_concept2)
        db_tag = self.tag_service.retrieve_or_create(tag)
        self.assertNotIn(db_tag.id, ids)
        self.assertNotEqual(db_tag, db_tags[1])

    def test_tag_retrieve_or_create_raises_on_invalid_arguments(self):
        # Create a database with three tags: a, b, c
        concept1 = Concept(title=u'test_concept1', description=u'test concept')
        plugin1 = Plugin(name=u'Plugin1', module=u'Module1')
        db_concept1 = self.concept_service.add(concept1)
        db_plugin1 = self.plugin_service.add(plugin1)
        db_tags = self._add_test_tags(values=[u'a', u'b', u'c'],
                                      concept=db_concept1,
                                      plugin=db_plugin1)

        # Try some creations that should not work
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_or_create(None)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_or_create('ID')
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_or_create(0)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_or_create(1)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_or_create(0L)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_or_create(1L)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_or_create(3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_or_create([])

        # Try some field changes that should not work
        with self.assertRaises(ObjectCubeException):
            tag = db_tags[1]
            self.tag_service.retrieve_or_create(tag)
        with self.assertRaises(ObjectCubeException):
            tag = db_tags[1]
            tag.id = None
            tag.plugin_id = None
            self.tag_service.retrieve_or_create(tag)
        with self.assertRaises(ObjectCubeException):
            tag = db_tags[1]
            tag.id = None
            tag.concept_id = None
            self.tag_service.retrieve_or_create(tag)

    def test_tag_retrieve_or_create_ambiguous_retrieval(self):
        db_concept = self.concept_service.add(
            Concept(title=u'test_concept', description=u'test concept'))
        db_plugin = self.plugin_service.add(Plugin(name=u'Plugin',
                                                   module=u'Module'))
        self._add_test_tags(values=['a', 'b', 'b', 'c'],
                            concept=db_concept, plugin=db_plugin)

        tag_b = self._create_test_tag(value=u'Tag_b',
                                      concept=db_concept, plugin=db_plugin)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_or_create(tag_b)

    # ==== update()

    def test_tag_update_works_with_legal_changes(self):
        # Create a database with three tags: a, b, c
        concept1 = Concept(title=u'test_concept1', description=u'test concept')
        concept2 = Concept(title=u'test_concept2', description=u'test concept')
        db_concept1 = self.concept_service.add(concept1)
        db_concept2 = self.concept_service.add(concept2)
        db_tags = self._add_test_tags(values=[u'a', u'b', u'c'],
                                      mutable=True, concept=db_concept1)

        after_value = u'New Value'
        tag = db_tags[0]
        tag.value = after_value
        self.tag_service.update(tag)
        db_tag = self.tag_service.retrieve_by_id(tag.id)
        self.assertEquals(db_tag, tag)
        self.assertEquals(db_tag.value, after_value)
        self.assertEquals(db_tag.description, db_tags[0].description)

        after_desc = u'New Desc'
        tag = db_tags[1]
        tag.description = after_desc
        self.tag_service.update(tag)
        db_tag = self.tag_service.retrieve_by_id(tag.id)
        self.assertEquals(db_tag, tag)
        self.assertEquals(db_tag.value, db_tags[1].value)
        self.assertEquals(db_tag.description, after_desc)

        tag = db_tags[2]
        tag.concept_id = db_concept2.id
        self.tag_service.update(tag)
        db_tag = self.tag_service.retrieve_by_id(tag.id)
        self.assertEquals(db_tag, tag)
        self.assertEquals(db_tag.value, db_tags[2].value)
        self.assertEquals(db_tag.description, db_tags[2].description)
        self.assertEquals(db_tag.concept_id, db_concept2.id)

        tag = db_tags[2]
        tag.type = 2L
        self.tag_service.update(tag)
        db_tag = self.tag_service.retrieve_by_id(tag.id)
        self.assertEquals(db_tag, tag)
        self.assertEquals(db_tag.value, db_tags[2].value)
        self.assertEquals(db_tag.description, db_tags[2].description)
        self.assertEquals(db_tag.type, 2L)

        db_tags2 = self.tag_service.retrieve()
        db_tags2.sort(lambda a, b: int(a.id) - int(b.id))
        db_tags.sort(lambda a, b: int(a.id) - int(b.id))
        self.assertEquals(db_tags, db_tags2)

    def test_tag_update_raises_on_invalid_arguments(self):
        with self.assertRaises(ObjectCubeException):
            self.tag_service.update(None)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.update([])

    def test_tag_update_with_illegal_tag_fails(self):
        # Create a database with three tags: a, b, c
        concept1 = Concept(title=u'test_concept1', description=u'test concept')
        concept2 = Concept(title=u'test_concept2', description=u'test concept')
        plugin1 = Plugin(name=u'Plugin1', module=u'Module1')
        plugin2 = Plugin(name=u'Plugin2', module=u'Module2')
        db_concept1 = self.concept_service.add(concept1)
        db_concept2 = self.concept_service.add(concept2)
        db_plugin1 = self.plugin_service.add(plugin1)
        db_plugin2 = self.plugin_service.add(plugin2)
        db_tags = self._add_test_tags(values=[u'a', u'b', u'c'],
                                      concept=db_concept1,
                                      plugin=db_plugin1)
        mutable_gen = self.tag_service.add(
            self._create_test_tag(value=u'd', mutable=True,
                                  concept=db_concept1,
                                  plugin=db_plugin1))

        # Test tags with non-existing ID
        with self.assertRaises(ObjectCubeException):
            tag = db_tags[0]
            tag.id = 30L
            self.tag_service.update(tag)
        with self.assertRaises(ObjectCubeException):
            tag = db_tags[0]
            tag.id = -1L
            self.tag_service.update(tag)

        # Test tags with illegal ID
        with self.assertRaises(ObjectCubeException):
            tag = db_tags[0]
            tag.id = None
            self.tag_service.update(tag)
        with self.assertRaises(ObjectCubeException):
            tag = db_tags[0]
            tag.id = 'ID'
            self.tag_service.update(tag)
        with self.assertRaises(ObjectCubeException):
            tag = db_tags[0]
            tag.id = []
            self.tag_service.update(tag)

        # Try to change immutable object
        with self.assertRaises(ObjectCubeException):
            tag = db_tags[1]
            tag.value = u'Cannot happen, sorry'
            self.tag_service.update(tag)
        with self.assertRaises(ObjectCubeException):
            tag = db_tags[1]
            tag.description = u'Cannot happen, sorry'
            self.tag_service.update(tag)

        # Try to change plugin generated object
        with self.assertRaises(ObjectCubeException):
            tag = mutable_gen
            tag.concept_id = db_concept2.id
            self.tag_service.update(tag)
        with self.assertRaises(ObjectCubeException):
            tag = mutable_gen
            tag.plugin_id = db_plugin2.id
            self.tag_service.update(tag)

    # ==== delete()

    def test_tag_delete_works_for_existing_tags(self):
        db_tags = self._add_test_tags([u'a', u'b', u'c'])

        victim = db_tags.pop(1)
        self.tag_service.delete(victim)

        db_tags2 = self.tag_service.retrieve()
        db_tags2.sort(lambda a, b: int(a.id) - int(b.id))
        db_tags.sort(lambda a, b: int(a.id) - int(b.id))
        self.assertEquals(db_tags, db_tags2)

    def test_tag_delete_raises_on_non_existing_tags(self):
        tags = self._add_test_tags([u'a', u'b', u'c'])
        db_tags = self.tag_service.retrieve()
        count = self.tag_service.count()

        with self.assertRaises(ObjectCubeException):
            victim = tags[0]
            victim.id = 200L
            self.tag_service.delete(victim)

        with self.assertRaises(ObjectCubeException):
            victim = tags[1]
            victim.id = None
            self.tag_service.delete(victim)

        with self.assertRaises(ObjectCubeException):
            victim = tags[2]
            victim.id = u'XXX'
            self.tag_service.delete(victim)

        self.assertEquals(count, self.tag_service.count())
        db_tags2 = self.tag_service.retrieve()
        db_tags2.sort(lambda a, b: int(a.id) - int(b.id))
        db_tags.sort(lambda a, b: int(a.id) - int(b.id))
        self.assertEquals(db_tags, db_tags2)

    def test_tag_delete_raises_on_invalid_arguments(self):
        with self.assertRaises(ObjectCubeException):
            self.tag_service.delete(None)

        with self.assertRaises(ObjectCubeException):
            self.tag_service.delete([])

    # ==== delete_by_id()

    def test_tag_delete_by_id_works_for_existing_tags(self):
        db_tags = self._add_test_tags([u'a', u'b', u'c'])

        victim = db_tags.pop(1)
        self.tag_service.delete_by_id(victim.id)

        db_tags2 = self.tag_service.retrieve()
        db_tags2.sort(lambda a, b: int(a.id) - int(b.id))
        db_tags.sort(lambda a, b: int(a.id) - int(b.id))
        self.assertEquals(db_tags, db_tags2)

    def test_tag_delete_by_id_raises_on_non_existing_tags(self):
        self._add_test_tags([u'a', u'b', u'c'])
        db_tags = self.tag_service.retrieve()
        count = self.tag_service.count()

        with self.assertRaises(ObjectCubeException):
            self.tag_service.delete_by_id(200L)

        self.assertEquals(count, self.tag_service.count())
        db_tags2 = self.tag_service.retrieve()
        db_tags2.sort(lambda a, b: int(a.id) - int(b.id))
        db_tags.sort(lambda a, b: int(a.id) - int(b.id))
        self.assertEquals(db_tags, db_tags2)

    def test_tag_delete_by_id_raises_on_invalid_arguments(self):
        with self.assertRaises(ObjectCubeException):
            self.tag_service.delete_by_id(None)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.delete_by_id([])
        with self.assertRaises(ObjectCubeException):
            self.tag_service.delete_by_id(None)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.delete_by_id(u'XXX')

    # ==== retrieve_by_id()

    def test_tag_retrieve_by_id_raises_exception_with_illegal_id(self):
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_id('1')

        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_id('Bjorn')

        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_id(None)

    def test_tag_retrieve_by_id_returns_nothing_with_non_existing_id(self):
        tag = self.tag_service.retrieve_by_id(-1L)
        self.assertEquals(tag, None, 'Tag returned where none should exist')

        tag = self.tag_service.retrieve_by_id(0L)
        self.assertEquals(tag, None, 'Tag returned where none should exist')

        tag = self.tag_service.retrieve_by_id(10000L)
        self.assertEquals(tag, None, 'Tag returned where none should exist')

    def test_tag_retrieve_by_id(self):
        t_in = self._create_test_tag()
        t_out = self.tag_service.add(t_in)
        t_from_db = self.tag_service.retrieve_by_id(t_out.id)
        self.assertEquals(t_from_db, t_out)

    # ==== retrieve()

    def test_tag_retrieve_returns_list(self):
        self.assertTrue(
            isinstance(self.tag_service.retrieve_by_value(u'23f'), list))

    def test_tag_retrieve_returns_empty_list(self):
        tags = self.tag_service.retrieve()
        self.assertTrue(len(tags) == 0,
                        msg=u'When no tags are in data store then retrieve '
                            u'should return empty list')

    def test_tag_retrieve_offset_limit(self):
        number_of_tags = 43
        max_fetch = 10L
        expected_id_set = self._tags_to_id_set(
            self._add_test_tags(range(number_of_tags)))
        self.assertEquals(number_of_tags, len(expected_id_set))

        all_retrieved_set = set()
        offset = 0L
        while True:
            tags = self.tag_service.retrieve(offset=offset, limit=max_fetch)
            retrieved_id_set = self._tags_to_id_set(tags)
            self.assertTrue(all_retrieved_set.isdisjoint(retrieved_id_set),
                            msg=u'ids overlap with previously retrieved tags '
                                u'when there should be no overlap')
            all_retrieved_set.update(retrieved_id_set)
            if len(tags) != max_fetch:
                self.assertEquals(number_of_tags % max_fetch, len(tags))
                break
            offset += max_fetch
        self.assertEquals(expected_id_set, all_retrieved_set)

    def test_tag_retrieve_limit_same_as_count(self):
        number_of_tags = 43
        max_fetch = 43L
        expected_id_set = self._tags_to_id_set(
            self._add_test_tags(range(number_of_tags)))
        self.assertEquals(number_of_tags, len(expected_id_set))

        all_retrieved_set = set()
        offset = 0L
        while True:
            tags = self.tag_service.retrieve(offset=offset, limit=max_fetch)
            retrieved_id_set = self._tags_to_id_set(tags)
            self.assertTrue(all_retrieved_set.isdisjoint(retrieved_id_set),
                            msg=u'ids overlap with previously retrieved tags '
                                u'when there should be no overlap')
            all_retrieved_set.update(retrieved_id_set)
            if len(tags) != max_fetch:
                self.assertEquals(number_of_tags % max_fetch, len(tags))
                break
            offset += max_fetch
        self.assertEquals(expected_id_set, all_retrieved_set)

    def test_tag_fetch_tag_outside_offset_return_empty_list(self):
        number_of_tags = 20
        for i in range(number_of_tags):
            self.tag_service.add(self._create_test_tag(value=unicode(i)))

        tags = self.tag_service.retrieve(offset=100L)
        self.assertTrue(len(tags) == 0,
                        msg=u'When selected offset which is outside of the '
                            'data set, then we will get an empty list')

    def test_tag_retrieve_raises_on_invalid_limit_offset(self):
        self.assertEquals(0, self.tag_service.count(),
                          msg='Database is not empty in beginning')
        self._add_test_tags(range(7))

        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve(offset=-1)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve(offset='0')
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve(offset='ID')
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve(offset=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve(offset=[])

        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve(limit=-1)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve(limit='0')
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve(limit='ID')
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve(limit=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve(limit=[])

    # ==== retrieve_by_plugin()

    def test_tag_retrieve_by_plugin(self):
        db_plugin = self.plugin_service.add(Plugin(name=u'test1_plugin',
                                                   module=u'dummy1_plugin'))
        self._add_test_tags(['41', '42', '42', '43'], plugin=db_plugin)
        no_plugin = self.plugin_service.add(Plugin(name=u'test2_plugin',
                                                   module=u'dummy2_plugin'))

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

    def test_tag_retrieve_by_plugin_raises_on_invalid_limit_offset(self):
        db_plugin = self.plugin_service.add(Plugin(name=u'test1_plugin',
                                                   module=u'dummy1_plugin'))
        self.assertEquals(0, self.tag_service.count(),
                          msg='Database is not empty in beginning')
        self._add_test_tags(range(7))

        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_plugin(plugin=db_plugin,
                                                offset=-1)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_plugin(plugin=db_plugin,
                                                offset='0')
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_plugin(plugin=db_plugin,
                                                offset='ID')
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_plugin(plugin=db_plugin,
                                                offset=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_plugin(plugin=db_plugin,
                                                offset=[])

        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_plugin(plugin=db_plugin,
                                                limit=-1)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_plugin(plugin=db_plugin,
                                                limit='0')
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_plugin(plugin=db_plugin,
                                                limit='ID')
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_plugin(plugin=db_plugin,
                                                limit=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_plugin(plugin=db_plugin,
                                                limit=[])

    def test_tag_retrieve_by_plugin_raises_on_no_id(self):
        self.assertEquals(0, self.tag_service.count(),
                          msg='Database is not empty in beginning')
        self._add_test_tags(range(7))
        db_plugin = self.plugin_service.add(Plugin(name=u'test1_plugin',
                                                   module=u'dummy1_plugin'))
        db_plugin.id = None

        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_plugin(plugin=db_plugin)

    # ==== retrieve_by_concept()

    def test_tag_retrieve_by_concept(self):
        db_concept = self.concept_service.add(
            Concept(title=u'test_concept', description=u'test concept'))
        db_plugin = self.plugin_service.add(Plugin(name=u'Plugin',
                                                   module=u'Module'))
        db_tags = self._add_test_tags(values=['41', '42', '42', '43'],
                                      mutable=True)

        retrieved_before = self.tag_service.retrieve_by_concept(db_concept)
        self.assertEquals(len(retrieved_before), 0)

        # add tag with concept or/and assign concept to some of the tags
        tag_ids_with_concept = set()
        new_tag = self._create_test_tag(value=u'new_concept_tag',
                                        concept=db_concept)
        tag_ids_with_concept.add(self.tag_service.add(new_tag).id)

        db_tags[0].concept_id = db_concept.id
        tag_ids_with_concept.add(self.tag_service.update(db_tags[0]).id)

        # by creating with retrieve_or_create..
        add_or_create_tag = self._create_test_tag(value=u'non_existing',
                                                  concept=db_concept,
                                                  plugin=db_plugin)
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

    def test_tag_retrieve_by_concept_raises_on_invalid_limit_offset(self):
        db_concept = self.concept_service.add(Concept(
            title=u'Title', description=u'Desc'))
        self.assertEquals(0, self.tag_service.count(),
                          msg='Database is not empty in beginning')
        self._add_test_tags(range(7))

        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_concept(concept=db_concept,
                                                 offset=-1)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_concept(concept=db_concept,
                                                 offset='0')
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_concept(concept=db_concept,
                                                 offset='ID')
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_concept(concept=db_concept,
                                                 offset=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_concept(concept=db_concept,
                                                 offset=[])

        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_concept(concept=db_concept,
                                                 limit=-1)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_concept(concept=db_concept,
                                                 limit='0')
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_concept(concept=db_concept,
                                                 limit='ID')
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_concept(concept=db_concept,
                                                 limit=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_concept(concept=db_concept,
                                                 limit=[])

    def test_tag_retrieve_by_concept_raises_on_no_id(self):
        self.assertEquals(0, self.tag_service.count(),
                          msg='Database is not empty in beginning')
        self._add_test_tags(range(7))
        db_concept = self.concept_service.add(Concept(
            title=u'Title', description=u'Desc'))
        db_concept.id = None

        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_concept(concept=db_concept)

    # ==== retrieve_by_value()

    def test_tag_retrieve_duplicate_returns_both(self):
        self.assertEquals(self.tag_service.count(), 0)
        self.tag_service.add(self._create_test_tag(value=u'Bjorn'))
        self.assertEquals(self.tag_service.count(), 1)
        self.tag_service.add(self._create_test_tag(value=u'Bjorn'))
        self.assertEquals(self.tag_service.count(), 2)
        retrieved = self.tag_service.retrieve_by_value(u'Bjorn')
        self.assertEquals(len(retrieved), 2)

    def test_tag_retrieve_by_value(self):
        retrieved_before = self.tag_service.retrieve_by_value(u'Tag_42')
        self.assertEquals(len(retrieved_before), 0)

        added_tags = self._add_test_tags([u'41', u'42', u'42', u'43'])
        relevant_tags = filter(lambda t: t.value == u'Tag_42', added_tags)
        retrieve_after = self.tag_service.retrieve_by_value(u'Tag_42')
        self.assertEquals(len(retrieve_after), 2)
        self.assertEquals(self._tags_to_id_set(relevant_tags),
                          self._tags_to_id_set(retrieve_after))

        low = self.tag_service.retrieve_by_value(u'Tag_42', 0L, 1L)
        high = self.tag_service.retrieve_by_value(u'Tag_42', 1L, 1L)
        out_of_range = self.tag_service.retrieve_by_value(u'Tag_42', 2L, 1L)
        self.assertEquals(self._tags_to_id_set(relevant_tags),
                          self._tags_to_id_set(low) |
                          self._tags_to_id_set(high))
        self.assertEquals(0, len(out_of_range))

    def test_tag_retrieve_by_value_raises_on_invalid_arguments(self):
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_value(None)

        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_value(1)

    def test_tag_retrieve_by_value_raises_on_invalid_limit_offset(self):
        self.assertEquals(0, self.tag_service.count(),
                          msg='Database is not empty in beginning')
        self._add_test_tags(range(7))

        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_value(value=u'Value',
                                               offset=-1)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_value(value=u'Value',
                                               offset='0')
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_value(value=u'Value',
                                               offset='ID')
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_value(value=u'Value',
                                               offset=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_value(value=u'Value',
                                               offset=[])

        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_value(value=u'Value',
                                               limit=-1)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_value(value=u'Value',
                                               limit='0')
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_value(value=u'Value',
                                               limit='ID')
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_value(value=u'Value',
                                               limit=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_value(value=u'Value',
                                               limit=[])

    # ==== retrieve_by_regex()

    def test_tag_retrieve_by_regex_value_offset_limit(self):
        number_of_tags = 43
        max_fetch = 10L
        db_tags = self._add_test_tags(range(number_of_tags))
        self.assertEquals(number_of_tags, len(db_tags))
        tags = []

        offset = 0L
        while True:
            tags = self.tag_service.retrieve_by_regex(
                value=db_tags[0].value+'$',
                offset=offset, limit=max_fetch
            )

            if len(tags) != max_fetch:
                break
            offset += max_fetch
        self.assertEquals(len(tags), 1,
                          'Returned too many tags--name should be unique')

        expected_id_set = self._tags_to_id_set(db_tags)
        self.assertEquals(number_of_tags, len(expected_id_set))
        all_retrieved_set = set()
        offset = 0L
        while True:
            tags = self.tag_service.retrieve_by_regex(
                value=u'Tag_',
                offset=offset, limit=max_fetch
            )

            retrieved_id_set = self._tags_to_id_set(tags)
            self.assertTrue(all_retrieved_set.isdisjoint(retrieved_id_set),
                            msg='Ids overlap with previously retrieved tags')
            all_retrieved_set.update(retrieved_id_set)
            if len(tags) != max_fetch:
                self.assertEquals(number_of_tags % max_fetch,
                                  len(tags))
                break
            offset += max_fetch
        self.assertEquals(expected_id_set, all_retrieved_set,
                          'Returned wrong concepts for regexp')

        offset = 0L
        while True:
            tags = self.tag_service.retrieve_by_regex(
                value=u'Unknown name',
                offset=offset, limit=max_fetch
            )

            if len(tags) != max_fetch:
                break
            offset += max_fetch
        self.assertEquals(len(tags), 0,
                          'Returned too many concepts--name should not exist')

    def test_concept_retrieve_by_regex_description_offset_limit(self):
        number_of_tags = 43
        max_fetch = 10L
        db_tags = self._add_test_tags(range(number_of_tags))
        self.assertEquals(number_of_tags, len(db_tags))
        tags = []

        offset = 0L
        while True:
            tags = self.tag_service.retrieve_by_regex(
                description=db_tags[0].description+'$',
                offset=offset, limit=max_fetch
            )

            if len(tags) != max_fetch:
                break
            offset += max_fetch
        self.assertEquals(len(tags), 1,
                          'Returned too many tags--name should be unique')

        expected_id_set = self._tags_to_id_set(db_tags)
        self.assertEquals(number_of_tags, len(expected_id_set))
        all_retrieved_set = set()
        offset = 0L
        while True:
            tags = self.tag_service.retrieve_by_regex(
                description=u'Desc_',
                offset=offset, limit=max_fetch
            )

            retrieved_id_set = self._tags_to_id_set(tags)
            self.assertTrue(all_retrieved_set.isdisjoint(retrieved_id_set),
                            msg='ids overlap with previously retrieved tags')
            all_retrieved_set.update(retrieved_id_set)
            if len(tags) != max_fetch:
                self.assertEquals(number_of_tags % max_fetch,
                                  len(tags))
                break
            offset += max_fetch
        self.assertEquals(expected_id_set, all_retrieved_set,
                          'Returned wrong concepts for regex')

        offset = 0L
        while True:
            tags = self.tag_service.retrieve_by_regex(
                description=u'Unknown name',
                offset=offset, limit=max_fetch
            )

            if len(tags) != max_fetch:
                break
            offset += max_fetch
        self.assertEquals(len(tags), 0,
                          'Returned too many concepts--name should not exist')

    def test_concept_retrieve_by_regex_title_description_offset_limit(self):
        number_of_tags = 43
        max_fetch = 10L
        db_tags = self._add_test_tags(range(number_of_tags))
        self.assertEquals(number_of_tags, len(db_tags))
        tags = []

        offset = 0L
        while True:
            tags = self.tag_service.retrieve_by_regex(
                value=db_tags[0].value+'$',
                description=db_tags[0].description+'$',
                offset=offset, limit=max_fetch
            )

            if len(tags) != max_fetch:
                break
            offset += max_fetch
        self.assertEquals(len(tags), 1,
                          'Returned too many tags--name should be unique')

        offset = 0L
        while True:
            tags = self.tag_service.retrieve_by_regex(
                value=u'Tag_15',
                description=u'Desc_',
                offset=offset, limit=max_fetch
            )

            if len(tags) != max_fetch:
                break
            offset += max_fetch
        self.assertEquals(len(tags), 1,
                          'Returned too many tags--name should be unique')

        expected_id_set = self._tags_to_id_set(db_tags)
        self.assertEquals(number_of_tags, len(expected_id_set))
        all_retrieved_set = set()
        offset = 0L
        while True:
            tags = self.tag_service.retrieve_by_regex(
                value=u'Tag_',
                description=u'Desc_',
                offset=offset, limit=max_fetch
            )

            retrieved_id_set = self._tags_to_id_set(tags)
            self.assertTrue(all_retrieved_set.isdisjoint(retrieved_id_set),
                            msg='ids overlap with previously retrieved tags')
            all_retrieved_set.update(retrieved_id_set)
            if len(tags) != max_fetch:
                self.assertEquals(number_of_tags % max_fetch,
                                  len(tags))
                break
            offset += max_fetch
        self.assertEquals(expected_id_set, all_retrieved_set,
                          'Returned wrong concepts for regexp')

        offset = 0L
        while True:
            tags = self.tag_service.retrieve_by_regex(
                value=u'Tag_',
                description=u'Unknown name',
                offset=offset, limit=max_fetch
            )

            if len(tags) != max_fetch:
                break
            offset += max_fetch
        self.assertEquals(len(tags), 0,
                          'Returned too many concepts--name should not exist')

    def test_concept_retrieve_by_regex_raises_on_invalid_regex(self):
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_regex(value=[])
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_regex(description=[])
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_regex()

    def test_concept_retrieve_by_regex_raises_on_invalid_limit_offset(self):
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_regex(value=u'X',
                                               offset=-1)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_regex(value=u'X',
                                               offset='0')
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_regex(value=u'X',
                                               offset='ID')
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_regex(value=u'X',
                                               offset=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_regex(value=u'X',
                                               offset=[])

        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_regex(value=u'X',
                                               limit=-1)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_regex(value=u'X',
                                               limit='0')
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_regex(value=u'X',
                                               limit='ID')
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_regex(value=u'X',
                                               limit=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.tag_service.retrieve_by_regex(value=u'X',
                                               limit=[])
