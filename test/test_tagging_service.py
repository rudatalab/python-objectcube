from random import shuffle
from base import ObjectCubeTestCase
from objectcube.data_objects import Object, Tag, Tagging, Plugin
from objectcube.exceptions import ObjectCubeException
from objectcube.factory import get_service
from types import IntType, LongType


class TestTaggingService(ObjectCubeTestCase):

    def __init__(self, *args, **kwargs):
        super(TestTaggingService, self).__init__(*args, **kwargs)
        self.tagging_service = get_service('TaggingService')
        self.plugin_service = get_service('PluginService')
        self.object_service = get_service('ObjectService')
        self.tag_service = get_service('TagService')

    def _create_test_object(self, name=u'N', digest=u'D'):
        return self.object_service.add(
            Object(name=name, digest=digest))

    def _create_test_objects(self, nrs):
        objects = []
        for nr in nrs:
            objects.append(self._create_test_object(
                u'Obj_'+unicode(nr),
                u'Dig_'+unicode(nr)))

        self.assertEquals(len(nrs), len(objects))
        return objects

    def _create_objects(self, nr_objects):
        return self._create_test_objects(range(0, nr_objects))

    def _create_test_tag(self, value=u'V', description=u'D'):
        return self.tag_service.add(
            Tag(value=value, description=description,
                mutable=False, type=1L))

    def _create_test_tags(self, nrs):
        tags = []
        shuffle(nrs)

        for nr in nrs:
            tags.append(self._create_test_tag(
                u'Tag_'+unicode(nr),
                u'Desc_'+unicode(nr)))

        self.assertEquals(len(nrs), len(tags))
        return tags

    def _create_tags(self, nr_tags):
        return self._create_test_tags(range(0, nr_tags))

    def _create_test_tagging(self, tag_id, object_id, meta,
                             plugin_id, plugin_set_id):
        tagging = Tagging(tag_id=tag_id,
                          object_id=object_id,
                          meta=meta,
                          plugin_id=plugin_id,
                          plugin_set_id=plugin_set_id)
        return self.tagging_service.add(tagging)

    def _create_test_taggings(self, tag_id, object_id, meta_list,
                              plugin_id, plugin_set_id):
        taggings = []
        shuffle(meta_list)

        for meta in meta_list:
            taggings.append(
                self._create_test_tagging(tag_id, object_id,
                                          u'Meta_'+unicode(meta),
                                          plugin_id, plugin_set_id))

        self.assertEquals(len(meta_list), len(taggings))
        return taggings

    def _create_taggings(self, tag_id, object_id, meta_count,
                         plugin_id, plugin_set_id):
        return self._create_test_taggings(tag_id,
                                          object_id,
                                          range(0, meta_count),
                                          plugin_id,
                                          plugin_set_id)

    def _tags_to_id_set(self, tags):
        """
        Helper to create id sets from tag list for testing union, etc.
        :param tags: List of tags to create id set from
        :return set containing the ids of the input tags
        """
        return set(map(lambda t: t.id, tags))

    def _set_up_db(self, nr_objects, nr_tags, nr_taggings):
        db_plugin = self.plugin_service.add(
            Plugin(name=u'Plugin', module=u'Description'))
        db_tags = self._create_tags(nr_tags)
        db_objects = self._create_objects(nr_objects)

        if isinstance(nr_taggings, (IntType, LongType)):
            db_taggings = self._create_taggings(db_tags[0].id,
                                                db_objects[0].id,
                                                nr_taggings,
                                                None, None)
        else:
            db_taggings = []
            plugin_set_id = 0L
            for n in nr_taggings:
                t, o = nr_taggings[n]
                plugin_set_id += 1L
                db_taggings.extend(
                    self._create_taggings(db_tags[t].id,
                                          db_objects[o].id,
                                          n,
                                          db_plugin.id,
                                          plugin_set_id))

        return db_plugin, db_tags, db_objects, db_taggings

    # ==== add()

    def test_tagging_add_increases_count(self):
        count = self.tagging_service.count()

        # Create a very small database
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, 1)

        self.assertEqual(len(db_taggings), 1,
                         msg='Wrong number of taggings')
        self.assertEqual(type(db_taggings[0]), Tagging,
                         msg='Tagging output of incorrect type')
        self.assertTrue(db_taggings[0].id, msg='Tagging ID invalid')
        self.assertEqual(db_taggings[0].object_id, db_objects[0].id,
                         msg='Tagging assigned to incorrect object')
        self.assertEqual(db_taggings[0].tag_id, db_tags[0].id,
                         msg='Tagging assigned to incorrect tag')
        self.assertEqual(count+1, self.tagging_service.count(),
                         msg='Tagging not added')

    def test_tagging_add_many_increases_count_correctly(self):
        count = self.tagging_service.count()
        tagging_dict = {10: (1, 1),
                        20: (3, 2),
                        1: (2, 1)}

        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(4, 4, tagging_dict)

        for cnt in tagging_dict:
            count += cnt

        self.assertEqual(len(db_taggings), count,
                         msg='Wrong number of taggings in output')
        self.assertEqual(count, self.tagging_service.count(),
                         msg='Wrong number of taggings in DB')

    def test_tagging_add_empty_meta_succeeds(self):
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, 0)
        count = self.tagging_service.count()

        tagging = Tagging(tag_id=db_tags[0].id,
                          object_id=db_objects[0].id,
                          meta=None)
        self.tagging_service.add(tagging)
        self.assertEquals(count + 1, self.tagging_service.count())

    def test_tagging_add_illegal_tagging_fails(self):
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, 0)
        count = self.tagging_service.count()

        # Test taggings with illegal taggings
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.add('ID')
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.add(True)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.add(False)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.add(1)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.add(db_tags[0])

        # Test objects with ID provided
        with self.assertRaises(ObjectCubeException):
            tagging = Tagging(id=1L,
                              tag_id=db_tags[0].id,
                              object_id=db_objects[0].id)
            self.tagging_service.add(tagging)
        with self.assertRaises(ObjectCubeException):
            tagging = Tagging(id=True,
                              tag_id=db_tags[0].id,
                              object_id=db_objects[0].id)
            self.tagging_service.add(tagging)
        with self.assertRaises(ObjectCubeException):
            tagging = Tagging(id=False,
                              tag_id=db_tags[0].id,
                              object_id=db_objects[0].id)
            self.tagging_service.add(tagging)

        # Test taggings with illegal tag ID
        with self.assertRaises(ObjectCubeException):
            tagging = Tagging(tag_id=0,
                              object_id=db_objects[0].id)
            self.tagging_service.add(tagging)
        with self.assertRaises(ObjectCubeException):
            tagging = Tagging(tag_id=1,
                              object_id=db_objects[0].id)
            self.tagging_service.add(tagging)
        with self.assertRaises(ObjectCubeException):
            tagging = Tagging(tag_id='ID',
                              object_id=db_objects[0].id)
            self.tagging_service.add(tagging)
        with self.assertRaises(ObjectCubeException):
            tagging = Tagging(tag_id=[],
                              object_id=db_objects[0].id)
            self.tagging_service.add(tagging)

        # Test objects with illegal object ID
        with self.assertRaises(ObjectCubeException):
            tagging = Tagging(tag_id=db_tags[0].id,
                              object_id=None)
            self.tagging_service.add(tagging)
        with self.assertRaises(ObjectCubeException):
            tagging = Tagging(tag_id=db_tags[0].id,
                              object_id=1)
            self.tagging_service.add(tagging)
        with self.assertRaises(ObjectCubeException):
            tagging = Tagging(tag_id=db_tags[0].id,
                              object_id='ID')
            self.tagging_service.add(tagging)
        with self.assertRaises(ObjectCubeException):
            tagging = Tagging(tag_id=db_tags[0].id,
                              object_id=False)
            self.tagging_service.add(tagging)

        # Test objects with illegal meta
        with self.assertRaises(ObjectCubeException):
            tagging = Tagging(tag_id=db_tags[0].id,
                              object_id=db_objects[0].id,
                              meta=0)
            self.tagging_service.add(tagging)
        with self.assertRaises(ObjectCubeException):
            tagging = Tagging(tag_id=db_tags[0].id,
                              object_id=db_objects[0].id,
                              meta=True)
            self.tagging_service.add(tagging)
        with self.assertRaises(ObjectCubeException):
            tagging = Tagging(tag_id=db_tags[0].id,
                              object_id=db_objects[0].id,
                              meta=3.1415297)
            self.tagging_service.add(tagging)
        with self.assertRaises(ObjectCubeException):
            tagging = Tagging(tag_id=db_tags[0].id,
                              object_id=db_objects[0].id,
                              meta=db_tags[0])
            self.tagging_service.add(tagging)

        # Test objects with illegal plugin
        with self.assertRaises(ObjectCubeException):
            tagging = Tagging(tag_id=db_tags[0].id,
                              object_id=db_objects[0].id,
                              plugin_id=1)
            self.tagging_service.add(tagging)
        with self.assertRaises(ObjectCubeException):
            tagging = Tagging(tag_id=db_tags[0].id,
                              object_id=db_objects[0].id,
                              plugin_id=True)
        with self.assertRaises(ObjectCubeException):
            tagging = Tagging(tag_id=db_tags[0].id,
                              object_id=db_objects[0].id,
                              plugin_id=False)
            self.tagging_service.add(tagging)
        with self.assertRaises(ObjectCubeException):
            tagging = Tagging(tag_id=db_tags[0].id,
                              object_id=db_objects[0].id,
                              plugin_id=3.1415297)
            self.tagging_service.add(tagging)
        with self.assertRaises(ObjectCubeException):
            tagging = Tagging(tag_id=db_tags[0].id,
                              object_id=db_objects[0].id,
                              plugin_id='ID')
            self.tagging_service.add(tagging)
        with self.assertRaises(ObjectCubeException):
            tagging = Tagging(tag_id=db_tags[0].id,
                              object_id=db_objects[0].id,
                              plugin_id=[])
            self.tagging_service.add(tagging)

        # Test objects with illegal plugin set id
        with self.assertRaises(ObjectCubeException):
            tagging = Tagging(tag_id=db_tags[0].id,
                              object_id=db_objects[0].id,
                              plugin_set_id=1)
            self.tagging_service.add(tagging)
        with self.assertRaises(ObjectCubeException):
            tagging = Tagging(tag_id=db_tags[0].id,
                              object_id=db_objects[0].id,
                              plugin_set_id=True)
        with self.assertRaises(ObjectCubeException):
            tagging = Tagging(tag_id=db_tags[0].id,
                              object_id=db_objects[0].id,
                              plugin_set_id=False)
            self.tagging_service.add(tagging)
        with self.assertRaises(ObjectCubeException):
            tagging = Tagging(tag_id=db_tags[0].id,
                              object_id=db_objects[0].id,
                              plugin_set_id=3.1415297)
            self.tagging_service.add(tagging)
        with self.assertRaises(ObjectCubeException):
            tagging = Tagging(tag_id=db_tags[0].id,
                              object_id=db_objects[0].id,
                              plugin_set_id='ID')
            self.tagging_service.add(tagging)
        with self.assertRaises(ObjectCubeException):
            tagging = Tagging(tag_id=db_tags[0].id,
                              object_id=db_objects[0].id,
                              plugin_set_id=[])
            self.tagging_service.add(tagging)

        self.assertEqual(count, self.tagging_service.count(),
                         msg='Illegal taggings added')

    def test_tagging_add_tagging_with_non_existing_data_fails(self):
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, 0)
        count = self.tagging_service.count()

        # Test with non-existent tags
        with self.assertRaises(ObjectCubeException):
            tagging = Tagging(tag_id=db_tags[0].id+10000L,
                              object_id=db_objects[0].id)
            self.tagging_service.add(tagging)
        with self.assertRaises(ObjectCubeException):
            tagging = Tagging(tag_id=db_tags[0].id,
                              object_id=db_objects[0].id+100L)
            self.tagging_service.add(tagging)
        with self.assertRaises(ObjectCubeException):
            tagging = Tagging(tag_id=db_tags[0].id+10000L,
                              object_id=db_objects[0].id+1000L)
            self.tagging_service.add(tagging)

        self.assertEqual(count, self.tagging_service.count(),
                         msg='Illegal taggings added')

    # ==== update()

    def test_update_works(self):
        # Initialize
        number_of_taggings = 43
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, number_of_taggings)

        # Update a tag
        meta = u'New Meta'
        db_taggings[0].meta = meta
        tagging = self.tagging_service.update(db_taggings[0])
        self.assertEquals(tagging.meta, meta,
                          msg='Update did not change meta')

        # Update a tag
        db_taggings[10].meta = None
        tagging = self.tagging_service.update(db_taggings[10])
        self.assertEquals(tagging.meta, None,
                          msg='Update did not remove meta')

        self.assertEquals(self.tagging_service.count(), number_of_taggings,
                          msg='Tagging set incorrectly modified')

    def test_update_with_non_string_meta_fails(self):
        # Initialize
        number_of_taggings = 43
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, number_of_taggings)

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

        self.assertEquals(self.tagging_service.count(), number_of_taggings,
                          msg='Tagging set incorrectly modified')

    def test_update_illegal_tagging_fails(self):
        # Initialize
        number_of_taggings = 43
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, number_of_taggings)

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
        self.assertEquals(self.tagging_service.count(), number_of_taggings,
                          msg='Tagging set modified')

    def test_update_without_id_fails(self):
        # Initialize
        number_of_taggings = 43
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, number_of_taggings)

        # Update for invalid taggings, should get errors
        db_taggings[0].id = None
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.update(db_taggings[0])

        # Make sure this correct, should not have affected tags
        self.assertEquals(self.tagging_service.count(), number_of_taggings,
                          msg='Tagging set modified')

    # ==== resolve()

    def test_resolve_by_legal_tag(self):
        # Initialize
        tagging_dict = {43: (0, 0)}
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(2, 2, tagging_dict)

        count = 0
        for cnt in tagging_dict:
            count += cnt

        # Make note of expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(count, len(expected_id_set))
        self.assertEquals(count, self.tagging_service.count())
        plugin_set_id = db_taggings[0].plugin_set_id

        # Resolve all the tags to the first one
        self.tagging_service.resolve(db_taggings[0])

        # Start retrieving
        all_retrieved_set = set()
        offset = 0L
        max_fetch = 10L
        while True:
            # Get the next max_fetch tags
            tags = self.tagging_service.retrieve(
                offset=offset, limit=max_fetch)

            # Get the new IDs and merge with the old set
            retrieved_id_set = self._tags_to_id_set(tags)
            all_retrieved_set.update(retrieved_id_set)

            # If length is different from max_fetch, we're done
            if len(tags) != max_fetch:
                break

            # Retrieved max_fetch
            offset += max_fetch

        # Make sure this correct, should only get one tag
        self.assertEquals(len(all_retrieved_set), 1,
                          msg='Plugin set was not resolved to a legal tag')

    def test_resolve_by_illegal_tag_changes_nothing(self):
        # Since only meta is updated, changes to tag_id or object_id do nothing
        # Initialize
        tagging_dict = {43: (0, 0)}
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(2, 2, tagging_dict)

        count = 0
        for cnt in tagging_dict:
            count += cnt

        # Make note of 4expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(count, len(expected_id_set))
        self.assertEquals(count, self.tagging_service.count())

        # Resolve all the tags to a non-existing tag, should fail
        tagging = db_taggings[0]
        tagging.tag_id += 2000L
        self.tagging_service.resolve(tagging)

        # Make sure this correct, have made no change
        tags = self.tagging_service.retrieve(
            offset=0L, limit=200L)

        # Make sure this correct, should only get one tag
        self.assertEquals(len(tags), 1,
                          msg='Plugin set not resolved')

    def test_resolve_a_non_existing_plugin_set_is_ok(self):
        # Initialize
        tagging_dict = {43: (0, 0)}
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(2, 2, tagging_dict)

        count = 0
        for cnt in tagging_dict:
            count += cnt

        # Make note of 4expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(count, len(expected_id_set))
        self.assertEquals(count, self.tagging_service.count())

        # Resolve all the tags from a non-existing plugin set to the first one
        tagging = Tagging(tag_id=db_tags[0].id,
                          object_id=db_objects[0].id,
                          meta=None,
                          plugin_id=db_plugin.id,
                          plugin_set_id=200L)
        self.tagging_service.resolve(tagging)

        # Start retrieving
        all_retrieved_set = set()
        max_fetch = 10L
        offset = 0L
        while True:
            # Get the next max_fetch tags
            tags = self.tagging_service.retrieve(
                offset=offset, limit=max_fetch)

            # Get the new IDs and merge with the old set
            retrieved_id_set = self._tags_to_id_set(tags)
            all_retrieved_set.update(retrieved_id_set)

            # If length is different from max_fetch, we're done
            if len(tags) != max_fetch:
                break

            # Retrieved max_fetch
            offset += max_fetch

        # Make sure this correct, should only get one tag
        self.assertEquals(len(all_retrieved_set), count+1)

    def test_resolve_illegal_plugin_set_fails(self):
        # Initialize
        tagging_dict = {43: (0, 0)}
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(2, 2, tagging_dict)

        count = 0
        for cnt in tagging_dict:
            count += cnt

        # Make note of expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(count, len(expected_id_set))
        self.assertEquals(count, self.tagging_service.count())

        # Resolve all the tags garbage, should fail
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.resolve(None)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.resolve(True)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.resolve(False)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.resolve('ID')
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.resolve(3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.resolve([])

        with self.assertRaises(ObjectCubeException):
            tagging = db_taggings[0]
            tagging.plugin_set_id = 3.1415297
            self.tagging_service.resolve(tagging)
        with self.assertRaises(ObjectCubeException):
            tagging = db_taggings[0]
            tagging.plugin_set_id = True
            self.tagging_service.resolve(tagging)
        with self.assertRaises(ObjectCubeException):
            tagging = db_taggings[0]
            tagging.plugin_set_id = 'ID'
            self.tagging_service.resolve(tagging)
        with self.assertRaises(ObjectCubeException):
            tagging = db_taggings[0]
            tagging.plugin_set_id = None
            self.tagging_service.resolve(tagging)

        # Make sure this correct, should not have changed anything
        self.assertEquals(self.tagging_service.count(), count,
                          msg='Illegal plugin set resolved')

    # ==== delete()

    def test_delete_works(self):
        # Initialize
        number_of_taggings = 43
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, number_of_taggings)

        # Delete a tag
        tagging = self.tagging_service.delete(db_taggings[0])
        self.assertEquals(tagging, None, msg='Delete returned tagging')

        # Delete a tag
        tagging = self.tagging_service.delete(db_taggings[3])
        self.assertEquals(tagging, None, msg='Delete returned tagging')

        self.assertEquals(self.tagging_service.count(), number_of_taggings-2,
                          msg='Tagging set incorrectly modified')

    def test_delete_non_existing_tagging_does_nothing(self):
        # Initialize
        number_of_taggings = 43
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, number_of_taggings)

        # Delete a tag
        with self.assertRaises(ObjectCubeException):
            tagging = db_taggings[0]
            tagging.id += 1000L
            self.tagging_service.delete(tagging)

        self.assertEquals(self.tagging_service.count(), number_of_taggings,
                          msg='Tagging set modified')

    def test_delete_tagging_twice_only_does_one(self):
        # Initialize
        number_of_taggings = 43
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, number_of_taggings)

        # Delete a tag
        tagging = self.tagging_service.delete(db_taggings[0])
        self.assertEquals(tagging, None, msg='Delete returned tagging')

        # Delete a tag again, should raise an error
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.delete(db_taggings[0])
        self.assertEquals(self.tagging_service.count(), number_of_taggings-1,
                          msg='Tagging set modified')

    def test_delete_illegal_tagging_fails(self):
        # Initialize
        number_of_taggings = 43
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, number_of_taggings)

        # Look for invalid tags, should get errors
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.delete(3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.delete('ID')
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.delete(db_tags[0])

        self.assertEquals(self.tagging_service.count(),
                          number_of_taggings,
                          msg='Tagging set modified')

    def test_delete_without_id_fails(self):
        # Initialize
        number_of_taggings = 43
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, number_of_taggings)

        # Look for invalid tags, should get errors
        tagging = db_taggings[0]
        tagging.id = None
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.delete(tagging)

        self.assertEquals(self.tagging_service.count(),
                          number_of_taggings,
                          msg='Tagging set modified')

    # ==== delete_by_id()

    def test_delete_by_id_works(self):
        # Initialize
        number_of_taggings = 43
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, number_of_taggings)

        # Delete a tagging
        tagging = self.tagging_service.delete_by_id(db_taggings[0].id)
        self.assertEquals(tagging, None, msg='Delete returned tagging')

        # Delete a tag
        tagging = self.tagging_service.delete_by_id(db_taggings[3].id)
        self.assertEquals(tagging, None, msg='Delete returned tagging')

        self.assertEquals(self.tagging_service.count(),
                          number_of_taggings-2,
                          msg='Tagging set incorrectly modified')

    def test_delete_by_id_non_existing_tagging_does_nothing(self):
        # Initialize
        number_of_taggings = 43
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, number_of_taggings)

        # Delete a tag
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.delete_by_id(db_taggings[0].id+1000L)

        self.assertEquals(self.tagging_service.count(),
                          number_of_taggings,
                          msg='Tagging set modified')

    def test_delete_by_id_tagging_twice_only_does_one(self):
        # Initialize
        number_of_taggings = 43
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, number_of_taggings)

        # Delete a tag
        tagging = self.tagging_service.delete_by_id(db_taggings[0].id)
        self.assertEquals(tagging, None, msg='Delete returned tagging')

        # Delete a tag again, should raise an error
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.delete_by_id(db_taggings[0].id)
        self.assertEquals(self.tagging_service.count(),
                          number_of_taggings-1,
                          msg='Tagging set modified')

    def test_delete_by_id_illegal_tagging_fails(self):
        # Initialize
        number_of_taggings = 43
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, number_of_taggings)

        # Look for invalid tags, should get errors
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.delete_by_id(3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.delete_by_id('ID')
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.delete_by_id(db_tags[0])

        self.assertEquals(self.tagging_service.count(),
                          number_of_taggings,
                          msg='Tagging set modified')

    # ==== delete_by_set_id()

    def test_delete_by_set_id_works(self):
        # Initialize
        tagging_dict = {1: (0, 0), 2: (1, 1)}
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(2, 2, tagging_dict)

        count = 0
        for cnt in tagging_dict:
            count += cnt

        # Delete a tagging
        tagging = self.tagging_service.delete_by_set_id(
            db_taggings[0].plugin_set_id)
        self.assertEquals(tagging, None, msg='Delete returned tagging')

        # Delete a tag
        tagging = self.tagging_service.delete_by_set_id(
            db_taggings[1].plugin_set_id)
        self.assertEquals(tagging, None, msg='Delete returned tagging')

        self.assertEquals(self.tagging_service.count(), 0,
                          msg='Tagging set incorrectly modified')

    def test_delete_by_set_id_non_existing_tagging_does_nothing(self):
        # Initialize
        tagging_dict = {1: (0, 0), 2: (1, 1)}
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(2, 2, tagging_dict)

        count = 0
        for cnt in tagging_dict:
            count += cnt

        # Delete a tag
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.delete_by_set_id(
                db_taggings[0].plugin_set_id+1000L)

        self.assertEquals(self.tagging_service.count(), count,
                          msg='Tagging set modified')

    def test_delete_by_set_id_tagging_twice_only_does_one(self):
        # Initialize
        tagging_dict = {1: (0, 0), 2: (1, 1)}
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(2, 2, tagging_dict)

        count = 0
        for cnt in tagging_dict:
            count += cnt

        # Delete a tag
        tagging = self.tagging_service.delete_by_set_id(
            db_taggings[0].plugin_set_id)
        self.assertEquals(tagging, None, msg='Delete returned tagging')

        # Delete a tag again, should raise an error
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.delete_by_set_id(
                db_taggings[0].plugin_set_id)
        self.assertEquals(self.tagging_service.count(), count-1,
                          msg='Tagging set modified')

    def test_delete_by_set_id_illegal_tagging_fails(self):
        # Initialize
        tagging_dict = {1: (0, 0), 2: (1, 1)}
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(2, 2, tagging_dict)

        count = 0
        for cnt in tagging_dict:
            count += cnt

        # Look for invalid tags, should get errors
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.delete_by_set_id(3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.delete_by_set_id('ID')
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.delete_by_set_id(db_tags[0])

        self.assertEquals(self.tagging_service.count(),
                          count,
                          msg='Tagging set modified')

    """
    # ==== retrieve_by_tag_id()

    def test_retrieve_by_tag_id_offset_limit(self):
        # Initialize
        count = self.tagging_service.count()
        number_of_taggings = 43
        max_fetch = 10L

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, number_of_taggings)

        # Make note of 4expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings,
                          self.tagging_service.count()-count)

        # Start retrieving
        all_retrieved_set = set()
        offset = 0L
        while True:
            # Get the next max_fetch tags
            tags = self.tagging_service.retrieve_by_tag_id(
                tag_id=db_tags[0].id,
                offset=offset, limit=max_fetch)

            # Get the new IDs and merge with the old set
            retrieved_id_set = self._tags_to_id_set(tags)
            self.assertTrue(all_retrieved_set.isdisjoint(retrieved_id_set),
                            msg='ids overlap with previously retrieved tags '
                                'when there should be no overlap')
            all_retrieved_set.update(retrieved_id_set)

            # If length is different from max_fetch, we're done
            if len(tags) != max_fetch:
                self.assertEquals(number_of_taggings % max_fetch, len(tags),
                                  msg='Did not get the correct list back')
                break

            # Retrieved max_fetch
            offset += max_fetch

        # Make sure this correct
        self.assertEquals(expected_id_set, all_retrieved_set,
                          msg='Did not get all the tagging list back')

    def test_retrieve_by_tag_id_limit_same_as_count(self):
        # Initialize
        count = self.tagging_service.count()
        number_of_taggings = 43L
        max_fetch = number_of_taggings

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, number_of_taggings)

        # Make note of 4expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings,
                          self.tagging_service.count()-count)

        # Start retrieving
        all_retrieved_set = set()
        offset = 0L
        while True:
            # Get the next max_fetch tags
            tags = self.tagging_service.retrieve_by_tag_id(
                tag_id=db_tags[0].id,
                offset=offset, limit=max_fetch)

            # Get the new IDs and merge with the old set
            retrieved_id_set = self._tags_to_id_set(tags)
            self.assertTrue(all_retrieved_set.isdisjoint(retrieved_id_set),
                            msg='ids overlap with previously retrieved tags'
                            ' when there should be no overlap')
            all_retrieved_set.update(retrieved_id_set)

            # If length is different from max_fetch, we're done
            if len(tags) != max_fetch:
                self.assertEquals(number_of_taggings % max_fetch, len(tags),
                                  msg='Did not get the correct list back')
                break

            # Retrieved max_fetch
            offset += max_fetch

        # Make sure this is correct
        self.assertEquals(expected_id_set, all_retrieved_set,
                          msg='Did not get all the tagging list back')

    def test_retrieve_by_id_non_existent_id_returns_no_results(self):
        count = self.tagging_service.count()
        number_of_taggings = 43
        max_fetch = 10L

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, number_of_taggings)

        # Make note of 4expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings,
                          self.tagging_service.count()-count)

        # Start retrieving
        all_retrieved_set = set()
        offset = 0L
        while True:
            # Get the next max_fetch tags
            tags = self.tagging_service.retrieve_by_tag_id(
                tag_id=db_tags[0].id+20000,
                offset=offset, limit=max_fetch)

            # Get the new IDs and merge with the old set
            retrieved_id_set = self._tags_to_id_set(tags)
            all_retrieved_set.update(retrieved_id_set)

            # If length is different from max_fetch, we're done
            if len(tags) != max_fetch:
                break

            # Retrieved max_fetch
            offset += max_fetch

        # Make sure this is correct
        self.assertEquals(set(), all_retrieved_set,
                          msg='Got some unintended tags back')
        self.assertEquals(0, len(all_retrieved_set),
                          msg='Got more than 0 tags back')

    def test_retrieve_by_id_wrong_id_returns_no_results(self):
        # Initialize
        count = self.tagging_service.count()
        number_of_taggings = 43L
        max_fetch = number_of_taggings

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, number_of_taggings)

        # Make note of expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings,
                          self.tagging_service.count()-count)

        # Start retrieving
        all_retrieved_set = set()
        offset = 0L
        while True:
            # Get the next max_fetch tags
            tags = self.tagging_service.retrieve_by_tag_id(
                tag_id=db_tags[1].id,
                offset=offset, limit=max_fetch)

            # Get the new IDs and merge with the old set
            retrieved_id_set = self._tags_to_id_set(tags)
            all_retrieved_set.update(retrieved_id_set)

            # If length is different from max_fetch, we're done
            if len(tags) != max_fetch:
                break

            # Retrieved max_fetch
            offset += max_fetch

        # Make sure this is correct
        self.assertEquals(set(), all_retrieved_set,
                          msg='Got some unintended tags back')
        self.assertEquals(0, len(all_retrieved_set),
                          msg='Got more than 0 tags back')

    def test_retrieve_by_id_invalid_id_throws_exception(self):
        # Initialize
        count = self.tagging_service.count()
        number_of_taggings = 43L

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, number_of_taggings)

        # Make note of expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings,
                          self.tagging_service.count()-count)

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
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, number_of_taggings)

        # Make note of expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings,
                          self.tagging_service.count()-count)

        # Start retrieving
        all_retrieved_set = set()
        offset = 0L
        while True:
            # Get the next max_fetch tags
            tags = self.tagging_service.retrieve_by_object_id(
                object_id=db_objects[0].id,
                offset=offset, limit=max_fetch)

            # Get the new IDs and merge with the old set
            retrieved_id_set = self._tags_to_id_set(tags)
            self.assertTrue(all_retrieved_set.isdisjoint(retrieved_id_set),
                            msg='ids overlap with previously retrieved tags'
                            ' when there should be no overlap')
            all_retrieved_set.update(retrieved_id_set)

            # If length is different from max_fetch, we're done
            if len(tags) != max_fetch:
                self.assertEquals(number_of_taggings % max_fetch, len(tags),
                                  msg='Did not get the correct list back')
                break

            # Retrieved max_fetch
            offset += max_fetch

        # Make sure this correct
        self.assertEquals(expected_id_set, all_retrieved_set,
                          msg='Did not get all the tagging list back')

    def test_retrieve_by_object_id_limit_same_as_count(self):
        # Initialize
        count = self.tagging_service.count()
        number_of_taggings = 43L
        max_fetch = number_of_taggings

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, number_of_taggings)

        # Make note of 4expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings,
                          self.tagging_service.count()-count)

        # Start retrieving
        all_retrieved_set = set()
        offset = 0L
        while True:
            # Get the next max_fetch tags
            tags = self.tagging_service.retrieve_by_object_id(
                object_id=db_objects[0].id,
                offset=offset, limit=max_fetch)

            # Get the new IDs and merge with the old set
            retrieved_id_set = self._tags_to_id_set(tags)
            self.assertTrue(all_retrieved_set.isdisjoint(retrieved_id_set),
                            msg='ids overlap with previously retrieved tags'
                            ' when there should be no overlap')
            all_retrieved_set.update(retrieved_id_set)

            # If length is different from max_fetch, we're done
            if len(tags) != max_fetch:
                self.assertEquals(number_of_taggings % max_fetch, len(tags),
                                  msg='Did not get the correct list back')
                break

            # Retrieved max_fetch
            offset += max_fetch

        # Make sure this is correct
        self.assertEquals(expected_id_set, all_retrieved_set,
                          msg='Did not get all the tagging list back')

    def test_retrieve_by_object_id_non_existent_id_returns_no_results(self):
        count = self.tagging_service.count()
        number_of_taggings = 43
        max_fetch = 10L

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, number_of_taggings)

        # Make note of 4expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings,
                          self.tagging_service.count()-count)

        # Start retrieving
        all_retrieved_set = set()
        offset = 0L
        while True:
            # Get the next max_fetch tags
            tags = self.tagging_service.retrieve_by_object_id(
                object_id=db_objects[0].id+20000,
                offset=offset, limit=max_fetch)

            # Get the new IDs and merge with the old set
            retrieved_id_set = self._tags_to_id_set(tags)
            all_retrieved_set.update(retrieved_id_set)

            # If length is different from max_fetch, we're done
            if len(tags) != max_fetch:
                break

            # Retrieved max_fetch
            offset += max_fetch

        # Make sure this is correct
        self.assertEquals(set(), all_retrieved_set,
                          msg='Got some unintended tags back')
        self.assertEquals(0, len(all_retrieved_set),
                          msg='Got more than 0 tags back')

    def test_retrieve_by_object_id_wrong_id_returns_no_results(self):
        # Initialize
        count = self.tagging_service.count()
        number_of_taggings = 43L
        max_fetch = number_of_taggings

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, number_of_taggings)

        # Make note of expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings,
                          self.tagging_service.count()-count)

        # Start retrieving
        all_retrieved_set = set()
        offset = 0L
        while True:
            # Get the next max_fetch tags
            tags = self.tagging_service.retrieve_by_object_id(
                object_id=db_objects[1].id,
                offset=offset, limit=max_fetch)

            # Get the new IDs and merge with the old set
            retrieved_id_set = self._tags_to_id_set(tags)
            all_retrieved_set.update(retrieved_id_set)

            # If length is different from max_fetch, we're done
            if len(tags) != max_fetch:
                break

            # Retrieved max_fetch
            offset += max_fetch

        # Make sure this is correct
        self.assertEquals(set(), all_retrieved_set,
                          msg='Got some unintended tags back')
        self.assertEquals(0, len(all_retrieved_set),
                          msg='Got more than 0 tags back')

    def test_retrieve_by_object_id_invalid_id_throws_exception(self):
        # Initialize
        count = self.tagging_service.count()
        number_of_taggings = 43L

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, number_of_taggings)

        # Make note of expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings,
                          self.tagging_service.count()-count)

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
        number_of_taggings = 43L
        max_fetch = 10L

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, number_of_taggings)

        # Make note of 4expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings,
                          self.tagging_service.count()-count)

        # Start retrieving
        all_retrieved_set = set()
        offset = 0L
        while True:
            # Get the next max_fetch tags
            tags = self.tagging_service.retrieve_by_set_id(
                plugin_set_id=db_taggings[0].plugin_set_id,
                offset=offset, limit=max_fetch)

            # Get the new IDs and merge with the old set
            retrieved_id_set = self._tags_to_id_set(tags)
            self.assertTrue(all_retrieved_set.isdisjoint(retrieved_id_set),
                            msg='ids overlap with previously retrieved tags'
                            ' when there should be no overlap')
            all_retrieved_set.update(retrieved_id_set)

            # If length is different from max_fetch, we're done
            if len(tags) != max_fetch:
                self.assertEquals(number_of_taggings % max_fetch, len(tags),
                                  msg='Did not get the correct list back')
                break

            # Retrieved max_fetch
            offset += max_fetch

        # Make sure this correct
        self.assertEquals(expected_id_set, all_retrieved_set,
                          msg='Did not get all the tagging list back')

    def test_retrieve_by_plugin_set_id_limit_same_as_count(self):
        # Initialize
        count = self.tagging_service.count()
        number_of_taggings = 43L
        max_fetch = number_of_taggings

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, number_of_taggings)

        # Make note of 4expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings,
                          self.tagging_service.count()-count)

        # Start retrieving
        all_retrieved_set = set()
        offset = 0L
        while True:
            # Get the next max_fetch tags
            tags = self.tagging_service.retrieve_by_set_id(
                plugin_set_id=db_taggings[0].plugin_set_id,
                offset=offset, limit=max_fetch)

            # Get the new IDs and merge with the old set
            retrieved_id_set = self._tags_to_id_set(tags)
            self.assertTrue(all_retrieved_set.isdisjoint(retrieved_id_set),
                            msg='ids overlap with previously retrieved tags'
                            ' when there should be no overlap')
            all_retrieved_set.update(retrieved_id_set)

            # If length is different from max_fetch, we're done
            if len(tags) != max_fetch:
                self.assertEquals(number_of_taggings % max_fetch, len(tags),
                                  msg='Did not get the correct list back')
                break

            # Retrieved max_fetch
            offset += max_fetch

        # Make sure this is correct
        self.assertEquals(expected_id_set, all_retrieved_set,
                          msg='Did not get all the tagging list back')

    def test_retrieve_by_plugin_set_id_non_existent_returns_no_results(self):
        count = self.tagging_service.count()
        number_of_taggings = 43L
        max_fetch = 10L

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, number_of_taggings)

        # Make note of 4expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings,
                          self.tagging_service.count()-count)

        # Start retrieving
        all_retrieved_set = set()
        offset = 0L
        while True:
            # Get the next max_fetch tags
            tags = self.tagging_service.retrieve_by_set_id(
                plugin_set_id=db_taggings[0].plugin_set_id+200,
                offset=offset, limit=max_fetch)

            # Get the new IDs and merge with the old set
            retrieved_id_set = self._tags_to_id_set(tags)
            all_retrieved_set.update(retrieved_id_set)

            # If length is different from max_fetch, we're done
            if len(tags) != max_fetch:
                break

            # Retrieved max_fetch
            offset += max_fetch

        # Make sure this is correct
        self.assertEquals(set(), all_retrieved_set,
                          msg='Got some unintended tags back')
        self.assertEquals(0, len(all_retrieved_set),
                          msg='Got more than 0 tags back')

    def test_retrieve_by_plugin_set_id_invalid_id_throws_exception(self):
        # Initialize
        count = self.tagging_service.count()
        number_of_taggings = 43L

        # Setup the DB with all taggings
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, number_of_taggings)

        # Make note of expected outcome
        expected_id_set = self._tags_to_id_set(db_taggings)
        self.assertEquals(number_of_taggings, len(expected_id_set))
        self.assertEquals(number_of_taggings,
                          self.tagging_service.count()-count)

        # Test various problematic inputs
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.retrieve_by_set_id(None)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.retrieve_by_set_id('Halli')
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.retrieve_by_set_id(3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.retrieve_by_set_id(Tag(id=1))

    def test_retrieve_by_id_works(self):
        # Initialize
        number_of_taggings = 43
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, number_of_taggings)

        # Look for a tag, see if I get it back
        tagging = self.tagging_service.retrieve_by_id(db_taggings[0].id)
        self.assertEquals(tagging, db_taggings[0], msg='Found wrong tagging')

        # Look for a tag, see if I get it back
        tagging = self.tagging_service.retrieve_by_id(db_taggings[3].id)
        self.assertEquals(tagging, db_taggings[3], msg='Found wrong tagging')

        self.assertEquals(self.tagging_service.count(), number_of_taggings,
                          msg='Tagging set modified')

    def test_retrieve_by_id_returns_empty_for_non_existing_id(self):
        # Initialize
        number_of_taggings = 43
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, number_of_taggings)

        # Look for a non-existing tag, should get None back
        tagging = self.tagging_service.retrieve_by_id(db_taggings[0].id+1000)
        self.assertEquals(tagging, None, msg='Found wrong tagging')

        self.assertEquals(self.tagging_service.count(), number_of_taggings,
                          msg='Tagging set modified')

    def test_retrieve_by_id_fails_for_invalid_id(self):
        # Initialize
        number_of_taggings = 43
        (db_plugin, db_tags, db_objects, db_taggings) = \
            self._set_up_db(1, 1, number_of_taggings)

        # Look for invalid tags, should get errors
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.retrieve_by_id(3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.retrieve_by_id('ID')
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.retrieve_by_id(Tag(id=db_tags[0]))
        with self.assertRaises(ObjectCubeException):
            self.tagging_service.retrieve_by_id(Tagging(id=db_taggings[0]))

        self.assertEquals(self.tagging_service.count(), number_of_taggings,
                          msg='Tagging set modified')
    """
