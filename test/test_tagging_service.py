from random import shuffle

from base import ObjectCubeTestCase
from objectcube.vo import Object, Tag, Tagging, Plugin
from objectcube.exceptions import ObjectCubeException, ObjectCubeException
from objectcube.factory import get_service


class TestTaggingService(ObjectCubeTestCase):

    def __init__(self, *args, **kwargs):
        super(TestTaggingService, self).__init__(*args, **kwargs)
        self.tagging_service = get_service('TaggingService')
        self.plugin_service = get_service('PluginService')
        self.object_service = get_service('ObjectService')
        self.tag_service = get_service('TagService')

    def _create_test_object(self, _name=u'', _digest=u''):
        return self.object_service.add(Object(id=None,
                                              name=_name,
                                              digest=_digest))

    def _create_test_objects(self, names):
        objects = []
        for name in names:
            objects.append(self._create_test_object(name, u'DIGEST'))

        self.assertEquals(len(names), len(objects))
        return objects

    def _create_objects(self):
        return self._create_test_objects([u'Fig', u'Img', u'Photo'])

    def _create_test_tag(self, _value=u'', _description=u''):
        return self.tag_service.add(Tag(id=None,
                                        value=_value,
                                        description=_description,
                                        mutable=False,
                                        type=0L,
                                        concept_id=None,
                                        plugin_id=None))

    def _create_test_tags(self, values):
        tags = []
        shuffle(values)

        for value in values:
            tags.append(self._create_test_tag(value, u'DESCRIPTION'))

        self.assertEquals(len(values), len(tags))
        return tags

    def _create_tags(self):
        return self._create_test_tags([
            u'People', u'Classmates', u'RU', u'Jack', u'Jill',
            u'MH', u'Bob', u'Alice', u'John'
        ])

    def _create_test_tagging(self, tag_id, object_id, meta, plugin_id, plugin_set_id):
        return self.tagging_service.add(tag_id,
                                        object_id,
                                        meta,
                                        plugin_id,
                                        plugin_set_id)

    def _create_test_taggings(self, tag_id, object_id, meta_list, plugin_id, plugin_set_id):
        taggings = []
        shuffle(meta_list)

        for meta in meta_list:
            taggings.append(self._create_test_tagging(tag_id, object_id, unicode(meta), plugin_id, plugin_set_id))

        self.assertEquals(len(meta_list), len(taggings))
        return taggings

    def _create_taggings(self, tag_id, object_id, meta_count, plugin_id, plugin_set_id):
        return self._create_test_taggings(tag_id,
                                          object_id,
                                          range(0, meta_count),
                                          Plugin(id=plugin_id),
                                          plugin_set_id)

    def _tags_to_id_set(self, tags):
        """
        Helper to create id sets from tag list for testing union, intersect, etc.
        :param tags: List of tags to create id set from
        :return set containing the ids of the input tags
        """
        return set(map(lambda t: t.id, tags))

    def _set_up_db(self, number_of_taggings):
        db_plugin = self.plugin_service.add(Plugin(name=u'Plugin', module=u'Description'))
        db_tags = self._create_tags()
        db_objects = self._create_objects()
        db_taggings = self._create_taggings(db_tags[0],
                                            db_objects[0],
                                            number_of_taggings,
                                            db_plugin.id, 1L)
        return db_plugin, db_tags, db_objects, db_taggings

    def test_tagging_add_increases_count(self):
        count = self.tagging_service.count()

        db_tags = self._create_tags()
        db_objects = self._create_objects()
        db_tagging = self.tagging_service.add(db_tags[0], db_objects[0], meta=None)
        self.assertEqual(type(db_tagging), Tagging, msg='Tagging output of incorrect type')
        self.assertTrue(db_tagging.id, msg='Tagging ID invalid')
        self.assertEqual(db_tagging.object_id, db_objects[0].id, msg='Tagging assigned to incorrect object')
        self.assertEqual(db_tagging.tag_id, db_tags[0].id, msg='Tagging assigned to incorrect tag')
        self.assertEqual(count+1, self.tagging_service.count(), msg='Tagging not added')

    def test_tagging_add_illegal_tagging_fails(self):
        number_of_taggings = 1
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(number_of_taggings)
        count = self.tagging_service.count()

        # Test tags with illegal ID
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.add(None, db_objects[0], meta=None)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.add(1, db_objects[0], meta=None)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.add(Tag(id='ID'), db_objects[0], meta=None)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.add(Tag(name='ID'), db_objects[0], meta=None)

        # Test with non-existent tags
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.add(Tag(id=db_tags[0].id+10000),
                                     db_objects[0], meta=None)

        # Test objects with illegal ID
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.add(db_tags[0], None, meta=None)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.add(db_tags[0], 1, meta=None)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.add(db_tags[0], Object(id='ID'), meta=None)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.add(db_tags[0], Object(name='ID'), meta=None)

        # Test with non-existent objects
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.add(db_tags[0],
                                     Object(id=db_objects[0].id+10000),
                                     meta=None)

        # Test objects with illegal meta
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.add(db_tags[0], db_objects[0], meta=0)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.add(db_tags[0], db_objects[0], meta=1)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.add(db_tags[0], db_objects[0], meta=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.add(db_tags[0], db_objects[0], db_tags[1])

        # Test objects with illegal plugin
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.add(db_tags[0], db_objects[0],
                                     meta=None, plugin=0)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.add(db_tags[0], db_objects[0],
                                     meta=None, plugin=1)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.add(db_tags[0], db_objects[0],
                                     meta=None, plugin=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.add(db_tags[0], db_objects[0],
                                     meta=None, plugin='ID')
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.add(db_tags[0], db_objects[0],
                                     meta=None, plugin=[])

        # Test with non-existent plugin
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.add(db_tags[0], Object(id=db_objects[0].id),
                                     meta=None,
                                     plugin=Plugin(id=long(db_plugin.id+1000)))

        # Test objects with illegal plugin set id
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.add(db_tags[0], db_objects[0], meta=None,
                                     plugin=None, plugin_set_id=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.add(db_tags[0], db_objects[0], meta=None,
                                     plugin=None, plugin_set_id='ID')
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.add(db_tags[0], db_objects[0], meta=None,
                                     plugin=None, plugin_set_id=db_tags[1])

        self.assertEqual(count, self.tagging_service.count(),
                         msg='Illegal taggings added')

    def test_retrieve_by_id_offset_limit(self):
        # Initialize
        count = self.tagging_service.count()
        number_of_taggings = 43
        max_fetch = 10L

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = self._set_up_db(number_of_taggings)

        # Make note of 4expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings, self.tagging_service.count()-count)

        # Start retrieving
        all_retrieved_set = set()
        offset = 0L
        while True:
            # Get the next max_fetch tags
            tags = self.tagging_service.retrieve_by_tag_id(tag_id=db_tags[0].id,
                                                           offset=offset,
                                                           limit=max_fetch)

            # Get the new IDs and merge with the old set
            retrieved_id_set = self._tags_to_id_set(tags)
            self.assertTrue(all_retrieved_set.isdisjoint(retrieved_id_set),
                            msg='ids overlap with previously retrieved tags'
                            ' when there should be no overlap')
            all_retrieved_set.update(retrieved_id_set)

            # If length is different from max_fetch, we're done
            if len(tags) != max_fetch:
                self.assertEquals(number_of_taggings % max_fetch, len(tags),
                                  msg='Did not get the correct final tagging list back')
                break

            # Retrieved max_fetch
            offset += max_fetch

        # Make sure this correct
        self.assertEquals(expected_id_set, all_retrieved_set, msg='Did not get all the tagging list back')

    def test_retrieve_by_id_limit_same_as_count(self):
        # Initialize
        count = self.tagging_service.count()
        number_of_taggings = 43L
        max_fetch = number_of_taggings

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = self._set_up_db(number_of_taggings)

        # Make note of 4expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings, self.tagging_service.count()-count)

        # Start retrieving
        all_retrieved_set = set()
        offset = 0L
        while True:
            # Get the next max_fetch tags
            tags = self.tagging_service.retrieve_by_tag_id(tag_id=db_tags[0].id,
                                                           offset=offset,
                                                           limit=max_fetch)

            # Get the new IDs and merge with the old set
            retrieved_id_set = self._tags_to_id_set(tags)
            self.assertTrue(all_retrieved_set.isdisjoint(retrieved_id_set),
                            msg='ids overlap with previously retrieved tags'
                            ' when there should be no overlap')
            all_retrieved_set.update(retrieved_id_set)

            # If length is different from max_fetch, we're done
            if len(tags) != max_fetch:
                self.assertEquals(number_of_taggings % max_fetch, len(tags),
                                  msg='Did not get the correct final tagging list back')
                break

            # Retrieved max_fetch
            offset += max_fetch

        # Make sure this is correct
        self.assertEquals(expected_id_set, all_retrieved_set, msg='Did not get all the tagging list back')

    def test_retrieve_by_id_non_existent_id_returns_no_results(self):
        count = self.tagging_service.count()
        number_of_taggings = 43
        max_fetch = 10L

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = self._set_up_db(number_of_taggings)

        # Make note of 4expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings, self.tagging_service.count()-count)

        # Start retrieving
        all_retrieved_set = set()
        offset = 0L
        while True:
            # Get the next max_fetch tags
            tags = self.tagging_service.retrieve_by_tag_id(tag_id=db_tags[0].id+20000,
                                                           offset=offset,
                                                           limit=max_fetch)

            # Get the new IDs and merge with the old set
            retrieved_id_set = self._tags_to_id_set(tags)
            all_retrieved_set.update(retrieved_id_set)

            # If length is different from max_fetch, we're done
            if len(tags) != max_fetch:
                break

            # Retrieved max_fetch
            offset += max_fetch

        # Make sure this is correct
        self.assertEquals(set(), all_retrieved_set, msg='Got some unintended tags back')
        self.assertEquals(0, len(all_retrieved_set), msg='Got more than 0 tags back')

    def test_retrieve_by_id_wrong_id_returns_no_results(self):
        # Initialize
        count = self.tagging_service.count()
        number_of_taggings = 43L
        max_fetch = number_of_taggings

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = self._set_up_db(number_of_taggings)

        # Make note of expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings, self.tagging_service.count()-count)

        # Start retrieving
        all_retrieved_set = set()
        offset = 0L
        while True:
            # Get the next max_fetch tags
            tags = self.tagging_service.retrieve_by_tag_id(tag_id=db_tags[1].id,
                                                           offset=offset,
                                                           limit=max_fetch)

            # Get the new IDs and merge with the old set
            retrieved_id_set = self._tags_to_id_set(tags)
            all_retrieved_set.update(retrieved_id_set)

            # If length is different from max_fetch, we're done
            if len(tags) != max_fetch:
                break

            # Retrieved max_fetch
            offset += max_fetch

        # Make sure this is correct
        self.assertEquals(set(), all_retrieved_set, msg='Got some unintended tags back')
        self.assertEquals(0, len(all_retrieved_set), msg='Got more than 0 tags back')

    def test_retrieve_by_id_invalid_id_throws_exception(self):
        # Initialize
        count = self.tagging_service.count()
        number_of_taggings = 43L
        max_fetch = number_of_taggings

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = self._set_up_db(number_of_taggings)

        # Make note of expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings, self.tagging_service.count()-count)

        # Test various problematic inputs
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.retrieve_by_tag_id(None)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.retrieve_by_tag_id('Halli')
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.retrieve_by_tag_id(3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.retrieve_by_tag_id(Tag(id=1))

    def test_retrieve_by_object_id_offset_limit(self):
        # Initialize
        count = self.tagging_service.count()
        number_of_taggings = 43
        max_fetch = 10L

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = self._set_up_db(number_of_taggings)

        # Make note of 4expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings, self.tagging_service.count()-count)

        # Start retrieving
        all_retrieved_set = set()
        offset = 0L
        while True:
            # Get the next max_fetch tags
            tags = self.tagging_service.retrieve_by_object_id(object_id=db_objects[0].id,
                                                              offset=offset,
                                                              limit=max_fetch)

            # Get the new IDs and merge with the old set
            retrieved_id_set = self._tags_to_id_set(tags)
            self.assertTrue(all_retrieved_set.isdisjoint(retrieved_id_set),
                            msg='ids overlap with previously retrieved tags'
                            ' when there should be no overlap')
            all_retrieved_set.update(retrieved_id_set)

            # If length is different from max_fetch, we're done
            if len(tags) != max_fetch:
                self.assertEquals(number_of_taggings % max_fetch, len(tags),
                                  msg='Did not get the correct final tagging list back')
                break

            # Retrieved max_fetch
            offset += max_fetch

        # Make sure this correct
        self.assertEquals(expected_id_set, all_retrieved_set, msg='Did not get all the tagging list back')

    def test_retrieve_by_object_id_limit_same_as_count(self):
        # Initialize
        count = self.tagging_service.count()
        number_of_taggings = 43L
        max_fetch = number_of_taggings

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = self._set_up_db(number_of_taggings)

        # Make note of 4expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings, self.tagging_service.count()-count)

        # Start retrieving
        all_retrieved_set = set()
        offset = 0L
        while True:
            # Get the next max_fetch tags
            tags = self.tagging_service.retrieve_by_object_id(object_id=db_objects[0].id,
                                                              offset=offset,
                                                              limit=max_fetch)

            # Get the new IDs and merge with the old set
            retrieved_id_set = self._tags_to_id_set(tags)
            self.assertTrue(all_retrieved_set.isdisjoint(retrieved_id_set),
                            msg='ids overlap with previously retrieved tags'
                            ' when there should be no overlap')
            all_retrieved_set.update(retrieved_id_set)

            # If length is different from max_fetch, we're done
            if len(tags) != max_fetch:
                self.assertEquals(number_of_taggings % max_fetch, len(tags),
                                  msg='Did not get the correct final tagging list back')
                break

            # Retrieved max_fetch
            offset += max_fetch

        # Make sure this is correct
        self.assertEquals(expected_id_set, all_retrieved_set, msg='Did not get all the tagging list back')

    def test_retrieve_by_object_id_non_existent_id_returns_no_results(self):
        count = self.tagging_service.count()
        number_of_taggings = 43
        max_fetch = 10L

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = self._set_up_db(number_of_taggings)

        # Make note of 4expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings, self.tagging_service.count()-count)

        # Start retrieving
        all_retrieved_set = set()
        offset = 0L
        while True:
            # Get the next max_fetch tags
            tags = self.tagging_service.retrieve_by_object_id(object_id=db_objects[0].id+20000,
                                                              offset=offset,
                                                              limit=max_fetch)

            # Get the new IDs and merge with the old set
            retrieved_id_set = self._tags_to_id_set(tags)
            all_retrieved_set.update(retrieved_id_set)

            # If length is different from max_fetch, we're done
            if len(tags) != max_fetch:
                break

            # Retrieved max_fetch
            offset += max_fetch

        # Make sure this is correct
        self.assertEquals(set(), all_retrieved_set, msg='Got some unintended tags back')
        self.assertEquals(0, len(all_retrieved_set), msg='Got more than 0 tags back')

    def test_retrieve_by_object_id_wrong_id_returns_no_results(self):
        # Initialize
        count = self.tagging_service.count()
        number_of_taggings = 43L
        max_fetch = number_of_taggings

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = self._set_up_db(number_of_taggings)

        # Make note of expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings, self.tagging_service.count()-count)

        # Start retrieving
        all_retrieved_set = set()
        offset = 0L
        while True:
            # Get the next max_fetch tags
            tags = self.tagging_service.retrieve_by_object_id(object_id=db_objects[1].id,
                                                              offset=offset,
                                                              limit=max_fetch)

            # Get the new IDs and merge with the old set
            retrieved_id_set = self._tags_to_id_set(tags)
            all_retrieved_set.update(retrieved_id_set)

            # If length is different from max_fetch, we're done
            if len(tags) != max_fetch:
                break

            # Retrieved max_fetch
            offset += max_fetch

        # Make sure this is correct
        self.assertEquals(set(), all_retrieved_set, msg='Got some unintended tags back')
        self.assertEquals(0, len(all_retrieved_set), msg='Got more than 0 tags back')

    def test_retrieve_by_object_id_invalid_id_throws_exception(self):
        # Initialize
        count = self.tagging_service.count()
        number_of_taggings = 43L
        max_fetch = number_of_taggings

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = self._set_up_db(number_of_taggings)

        # Make note of expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings, self.tagging_service.count()-count)

        # Test various problematic inputs
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.retrieve_by_object_id(None)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.retrieve_by_object_id('Halli')
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.retrieve_by_object_id(3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.retrieve_by_object_id(Tag(id=1))

    def test_retrieve_by_plugin_set_id_offset_limit(self):
        # Initialize
        count = self.tagging_service.count()
        number_of_taggings = 43
        max_fetch = 10L

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = self._set_up_db(number_of_taggings)

        # Make note of 4expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings, self.tagging_service.count()-count)

        # Start retrieving
        all_retrieved_set = set()
        offset = 0L
        while True:
            # Get the next max_fetch tags
            tags = self.tagging_service.retrieve_by_set_id(plugin_set_id=db_taggings[0].plugin_set_id,
                                                           offset=offset,
                                                           limit=max_fetch)

            # Get the new IDs and merge with the old set
            retrieved_id_set = self._tags_to_id_set(tags)
            self.assertTrue(all_retrieved_set.isdisjoint(retrieved_id_set),
                            msg='ids overlap with previously retrieved tags'
                            ' when there should be no overlap')
            all_retrieved_set.update(retrieved_id_set)

            # If length is different from max_fetch, we're done
            if len(tags) != max_fetch:
                self.assertEquals(number_of_taggings % max_fetch, len(tags),
                                  msg='Did not get the correct final tagging list back')
                break

            # Retrieved max_fetch
            offset += max_fetch

        # Make sure this correct
        self.assertEquals(expected_id_set, all_retrieved_set, msg='Did not get all the tagging list back')

    def test_retrieve_by_plugin_set_id_limit_same_as_count(self):
        # Initialize
        count = self.tagging_service.count()
        number_of_taggings = 43L
        max_fetch = number_of_taggings

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = self._set_up_db(number_of_taggings)

        # Make note of 4expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings, self.tagging_service.count()-count)

        # Start retrieving
        all_retrieved_set = set()
        offset = 0L
        while True:
            # Get the next max_fetch tags
            tags = self.tagging_service.retrieve_by_set_id(plugin_set_id=db_taggings[0].plugin_set_id,
                                                           offset=offset,
                                                           limit=max_fetch)

            # Get the new IDs and merge with the old set
            retrieved_id_set = self._tags_to_id_set(tags)
            self.assertTrue(all_retrieved_set.isdisjoint(retrieved_id_set),
                            msg='ids overlap with previously retrieved tags'
                            ' when there should be no overlap')
            all_retrieved_set.update(retrieved_id_set)

            # If length is different from max_fetch, we're done
            if len(tags) != max_fetch:
                self.assertEquals(number_of_taggings % max_fetch, len(tags),
                                  msg='Did not get the correct final tagging list back')
                break

            # Retrieved max_fetch
            offset += max_fetch

        # Make sure this is correct
        self.assertEquals(expected_id_set, all_retrieved_set, msg='Did not get all the tagging list back')

    def test_retrieve_by_plugin_set_id_non_existent_id_returns_no_results(self):
        count = self.tagging_service.count()
        number_of_taggings = 43
        max_fetch = 10L

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = self._set_up_db(number_of_taggings)

        # Make note of 4expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings, self.tagging_service.count()-count)

        # Start retrieving
        all_retrieved_set = set()
        offset = 0L
        while True:
            # Get the next max_fetch tags
            tags = self.tagging_service.retrieve_by_set_id(plugin_set_id=db_taggings[0].plugin_set_id+200,
                                                           offset=offset,
                                                           limit=max_fetch)

            # Get the new IDs and merge with the old set
            retrieved_id_set = self._tags_to_id_set(tags)
            all_retrieved_set.update(retrieved_id_set)

            # If length is different from max_fetch, we're done
            if len(tags) != max_fetch:
                break

            # Retrieved max_fetch
            offset += max_fetch

        # Make sure this is correct
        self.assertEquals(set(), all_retrieved_set, msg='Got some unintended tags back')
        self.assertEquals(0, len(all_retrieved_set), msg='Got more than 0 tags back')

    def test_retrieve_by_plugin_set_id_invalid_id_throws_exception(self):
        # Initialize
        count = self.tagging_service.count()
        number_of_taggings = 43L
        max_fetch = number_of_taggings

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = self._set_up_db(number_of_taggings)

        # Make note of expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings, self.tagging_service.count()-count)

        # Test various problematic inputs
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.retrieve_by_set_id(None)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.retrieve_by_set_id('Halli')
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.retrieve_by_set_id(3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.retrieve_by_set_id(Tag(id=1))

    def test_resolve_by_legal_tag(self):
        # Initialize
        count = self.tagging_service.count()
        number_of_taggings = 43
        max_fetch = 10L

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = self._set_up_db(number_of_taggings)

        # Make note of 4expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings, self.tagging_service.count()-count)

        # Resolve all the tags to the first one
        self.tagging_service.resolve(tag=db_tags[0],
                                     object=db_objects[0],
                                     meta=u'NEW TAGGING',
                                     plugin=db_plugin,
                                     plugin_set_id=db_taggings[0].plugin_set_id)

        # Start retrieving
        all_retrieved_set = set()
        offset = 0L
        while True:
            # Get the next max_fetch tags
            tags = self.tagging_service.retrieve_by_set_id(plugin_set_id=db_taggings[0].plugin_set_id,
                                                           offset=offset,
                                                           limit=max_fetch)

            # Get the new IDs and merge with the old set
            retrieved_id_set = self._tags_to_id_set(tags)
            all_retrieved_set.update(retrieved_id_set)

            # If length is different from max_fetch, we're done
            if len(tags) != max_fetch:
                break

            # Retrieved max_fetch
            offset += max_fetch

        # Make sure this correct, should only get one tag
        self.assertEquals(len(all_retrieved_set), 1, msg='Plugin set was not resolved to a legal tag')

    def test_resolve_by_illegal_tag(self):
        # Initialize
        count = self.tagging_service.count()
        number_of_taggings = 43
        max_fetch = 10L

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = self._set_up_db(number_of_taggings)

        # Make note of 4expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings, self.tagging_service.count()-count)

        # Resolve all the tags to a non-existing tag, should fail
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.resolve(tag=Tag(id=20000),
                                         object=db_objects[0],
                                         meta='NEW TAGGING',
                                         plugin=db_plugin,
                                         plugin_set_id=db_taggings[0].plugin_set_id)

        # Start retrieving
        all_retrieved_set = set()
        offset = 0L
        while True:
            # Get the next max_fetch tags
            tags = self.tagging_service.retrieve_by_set_id(plugin_set_id=db_taggings[0].plugin_set_id,
                                                           offset=offset,
                                                           limit=max_fetch)

            # Get the new IDs and merge with the old set
            retrieved_id_set = self._tags_to_id_set(tags)
            all_retrieved_set.update(retrieved_id_set)

            # If length is different from max_fetch, we're done
            if len(tags) != max_fetch:
                break

            # Retrieved max_fetch
            offset += max_fetch

        # Make sure this correct, should only get one tag
        self.assertEquals(len(all_retrieved_set), number_of_taggings, msg='Plugin set resolved to an illegal tag')

    def test_resolve_a_non_existing_plugin_set_is_ok(self):
        # Initialize
        count = self.tagging_service.count()
        number_of_taggings = 43
        max_fetch = 10L

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = self._set_up_db(number_of_taggings)

        # Make note of 4expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings, self.tagging_service.count()-count)

        # Resolve all the tags from a non-existing plugin set to the first one
        self.tagging_service.resolve(tag=db_tags[0],
                                     object=db_objects[0],
                                     meta=u'NEW TAGGING',
                                     plugin=db_plugin,
                                     plugin_set_id=db_taggings[0].plugin_set_id+100)

        # Start retrieving
        all_retrieved_set = set()
        offset = 0L
        while True:
            # Get the next max_fetch tags
            tags = self.tagging_service.retrieve_by_set_id(plugin_set_id=db_taggings[0].plugin_set_id+100,
                                                           offset=offset,
                                                           limit=max_fetch)

            # Get the new IDs and merge with the old set
            retrieved_id_set = self._tags_to_id_set(tags)
            all_retrieved_set.update(retrieved_id_set)

            # If length is different from max_fetch, we're done
            if len(tags) != max_fetch:
                break

            # Retrieved max_fetch
            offset += max_fetch

        # Make sure this correct, should only get one tag
        self.assertEquals(len(all_retrieved_set), 1, msg='Plugin set resolved to an illegal tag')

    def test_resolve_illegal_plugin_set_fails(self):
        # Initialize
        count = self.tagging_service.count()
        number_of_taggings = 43
        max_fetch = 10L

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = self._set_up_db(number_of_taggings)

        # Make note of expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings, self.tagging_service.count()-count)

        # Resolve all the tags to a non-existing tag, should fail
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.resolve(tag=db_tags[0],
                                         object=db_objects[0],
                                         meta=u'NEW TAGGING',
                                         plugin=db_plugin,
                                         plugin_set_id=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.resolve(tag=db_tags[0],
                                         object=db_objects[0],
                                         meta=u'NEW TAGGING',
                                         plugin=db_plugin,
                                         plugin_set_id='ID')
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.resolve(tag=db_tags[0],
                                         object=db_objects[0],
                                         meta=u'NEW TAGGING',
                                         plugin=db_plugin,
                                         plugin_set_id=db_tags[1])

        # Make sure this correct, should only get one tag
        self.assertEquals(self.tagging_service.count(), number_of_taggings, msg='Illegal plugin set resolved')

    def test_delete_an_existing_plugin_set_is_ok(self):
        # Initialize
        count = self.tagging_service.count()
        number_of_taggings = 43
        max_fetch = 10L

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = self._set_up_db(number_of_taggings)

        # Make note of 4expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings, self.tagging_service.count()-count)

        # Delete the plugin set
        self.tagging_service.delete_by_set_id(plugin_set_id=db_taggings[0].plugin_set_id)

        # Start retrieving
        all_retrieved_set = set()
        offset = 0L
        while True:
            # Get the next max_fetch tags
            tags = self.tagging_service.retrieve_by_set_id(plugin_set_id=db_taggings[0].plugin_set_id,
                                                           offset=offset,
                                                           limit=max_fetch)

            # Get the new IDs and merge with the old set
            retrieved_id_set = self._tags_to_id_set(tags)
            all_retrieved_set.update(retrieved_id_set)

            # If length is different from max_fetch, we're done
            if len(tags) != max_fetch:
                break

            # Retrieved max_fetch
            offset += max_fetch

        # Make sure this correct, should only get one tag
        self.assertEquals(len(all_retrieved_set), 0, msg='Plugin set was not deleted')

    def test_delete_an_non_existing_plugin_set_is_ok(self):
        # Initialize
        number_of_taggings = 43
        (db_plugin, db_tags, db_objects, db_taggings) = self._set_up_db(number_of_taggings)

        # Delete a non-existing set, nothing should happen
        self.tagging_service.delete_by_set_id(plugin_set_id=db_taggings[0].plugin_set_id+10000)

        # Check outcome
        self.assertEquals(self.tagging_service.count(), number_of_taggings, msg='Plugin set should not have changed')

    def test_delete_illegal_plugin_set_fails(self):
        # Initialize
        number_of_taggings = 43

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = self._set_up_db(number_of_taggings)

        # Resolve all the tags to a non-existing tag, should fail
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.delete_by_set_id(plugin_set_id=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.delete_by_set_id(plugin_set_id='ID')
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.delete_by_set_id(plugin_set_id=db_tags[1])

        # Make sure this correct, should only get one tag
        self.assertEquals(self.tagging_service.count(), number_of_taggings, msg='Illegal plugin set deleted')

    def test_retrieve_by_id_works(self):
        # Initialize
        number_of_taggings = 43
        (db_plugin, db_tags, db_objects, db_taggings) = self._set_up_db(number_of_taggings)

        # Look for a tag, see if I get it back
        tagging = self.tagging_service.retrieve_by_id(db_taggings[0].id)
        self.assertEquals(tagging, db_taggings[0], msg='Found wrong tagging')

        # Look for a tag, see if I get it back
        tagging = self.tagging_service.retrieve_by_id(db_taggings[3].id)
        self.assertEquals(tagging, db_taggings[3], msg='Found wrong tagging')

        self.assertEquals(self.tagging_service.count(), number_of_taggings, msg='Tagging set modified')

    def test_retrieve_by_id_returns_empty_for_non_existing_id(self):
        # Initialize
        number_of_taggings = 43
        (db_plugin, db_tags, db_objects, db_taggings) = self._set_up_db(number_of_taggings)

        # Look for a non-existing tag, should get None back
        tagging = self.tagging_service.retrieve_by_id(db_taggings[0].id+1000)
        self.assertEquals(tagging, None, msg='Found wrong tagging')

        self.assertEquals(self.tagging_service.count(), number_of_taggings, msg='Tagging set modified')

    def test_retrieve_by_id_fails_for_invalid_id(self):
        # Initialize
        number_of_taggings = 43
        (db_plugin, db_tags, db_objects, db_taggings) = self._set_up_db(number_of_taggings)

        # Look for invalid tags, should get errors
        with self.assertRaises(ObjectCubeException):
            tagging = self.tagging_service.retrieve_by_id(3.1415297)
        with self.assertRaises(ObjectCubeException):
            tagging = self.tagging_service.retrieve_by_id('ID')
        with self.assertRaises(ObjectCubeException):
            tagging = self.tagging_service.retrieve_by_id(Tag(id=db_tags[0]))
        with self.assertRaises(ObjectCubeException):
            tagging = self.tagging_service.retrieve_by_id(Tagging(id=db_taggings[0]))

        self.assertEquals(self.tagging_service.count(), number_of_taggings, msg='Tagging set modified')

    def test_delete_works(self):
        # Initialize
        number_of_taggings = 43
        (db_plugin, db_tags, db_objects, db_taggings) = self._set_up_db(number_of_taggings)

        # Delete a tag
        tagging = self.tagging_service.delete(db_taggings[0])
        self.assertEquals(tagging, None, msg='Delete returned tagging')

        # Delete a tag
        tagging = self.tagging_service.delete(db_taggings[3])
        self.assertEquals(tagging, None, msg='Delete returned tagging')

        self.assertEquals(self.tagging_service.count(), number_of_taggings - 2, msg='Tagging set incorrectly modified')

    def test_delete_non_existing_tagging_does_nothing(self):
        # Initialize
        number_of_taggings = 43
        (db_plugin, db_tags, db_objects, db_taggings) = self._set_up_db(number_of_taggings)

        # Delete a tag
        tagging = self.tagging_service.delete(Tagging(id=db_taggings[0].id+1000))
        self.assertEquals(tagging, None, msg='Delete returned tagging')

        self.assertEquals(self.tagging_service.count(), number_of_taggings, msg='Tagging set modified')

    def test_delete_tagging_twice_only_does_one(self):
        # Initialize
        number_of_taggings = 43
        (db_plugin, db_tags, db_objects, db_taggings) = self._set_up_db(number_of_taggings)

        # Delete a tag
        tagging = self.tagging_service.delete(db_taggings[0])
        self.assertEquals(tagging, None, msg='Delete returned tagging')

        # Delete a tag again
        tagging = self.tagging_service.delete(db_taggings[0])
        self.assertEquals(tagging, None, msg='Delete returned tagging')

        self.assertEquals(self.tagging_service.count(), number_of_taggings - 1, msg='Tagging set modified')

    def test_delete_illegal_tagging_fails(self):
        # Initialize
        number_of_taggings = 43
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(number_of_taggings)

        # Look for invalid tags, should get errors
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.delete(3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.delete('ID')
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.delete(Tag(id=db_tags[0]))

        self.assertEquals(self.tagging_service.count(),
                          number_of_taggings, msg='Tagging set modified')

    def test_update_works(self):
        # Initialize
        number_of_taggings = 43
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(number_of_taggings)

        # Update a tag
        meta = u'NEW META'
        db_taggings[0].meta = meta
        tagging = self.tagging_service.update(db_taggings[0])
        self.assertEquals(tagging.meta, meta, msg='Update did not change meta')

        # Update a tag
        db_taggings[10].meta = None
        tagging = self.tagging_service.update(db_taggings[10])
        self.assertEquals(tagging.meta, None, msg='Update did not change meta')

        self.assertEquals(self.tagging_service.count(), number_of_taggings, msg='Tagging set incorrectly modified')

    def test_update_with_non_string_meta_fails(self):
        # Initialize
        number_of_taggings = 43
        (db_plugin, db_tags, db_objects, db_taggings) = self._set_up_db(number_of_taggings)

        with self.assertRaises(ObjectCubeException):
            db_taggings[0].meta = 0
            self.tagging_service.update(db_taggings[0])

        with self.assertRaises(ObjectCubeException):
            db_taggings[0].meta = 1
            self.tagging_service.update(db_taggings[0])

        with self.assertRaises(ObjectCubeException):
            db_taggings[0].meta = 3.1415297
            self.tagging_service.update(db_taggings[0])

        with self.assertRaises(ObjectCubeException):
            db_taggings[0].meta = db_tags[0]
            self.tagging_service.update(db_taggings[0])

        self.assertEquals(self.tagging_service.count(), number_of_taggings, msg='Tagging set incorrectly modified')

    def test_update_illegal_tagging_fails(self):
        # Initialize
        number_of_taggings = 43
        (db_plugin, db_tags, db_objects, db_taggings) = self._set_up_db(number_of_taggings)

        # Update for invalid taggings, should get errors
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.update(3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.update('ID')
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.update(Tag(id=db_tags[0]))
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.update(Tagging(tag_id=1))

        # Make sure this correct, should not have affected tags
        self.assertEquals(self.tagging_service.count(), number_of_taggings, msg='Tagging set modified')

