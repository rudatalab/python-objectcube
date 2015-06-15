from objectcube.factory import get_service
from objectcube.exceptions import ObjectCubeException
from objectcube.utils import md5_from_value
from objectcube.vo import Plugin, Tag
from base import ObjectCubeTestCase
from types import IntType, LongType
from random import shuffle

class TestPluginService(ObjectCubeTestCase):

    def __init__(self, *args, **kwargs):
        super(TestPluginService, self).__init__(*args, **kwargs)
        self.plugin_service = get_service('PluginService')

    def _create_plugins(self, num_plugins, name_prefix='Plugin_'):
        plugins = []
        for i in range(num_plugins):
            plugins.append(self.plugin_service.add(
                Plugin(
                    name='{0}{1}'.format(name_prefix, i),
                    module='return pass; {0}'.format(i)
                )
            ))
        return plugins

    def test_starts_with_no_plugin(self):
        self.assertEquals(0, self.plugin_service.count(), msg='Database is not empty in beginning')
        self.assertTrue(isinstance(self.plugin_service.count(), (IntType, LongType)),
                        msg='The count function should return a number')

    def test_plugin_add_increases_count(self):
        self.assertEquals(0, self.plugin_service.count(), msg='Database is not empty in beginning')
        db_plugin = self.plugin_service.add(Plugin(name='Plugin', module='Module'))
        self.assertEquals(1, self.plugin_service.count(), msg='Plugin is not added to database')
        self.assertIsInstance(db_plugin, Plugin, msg='')

    def test_plugin_retrieve_raises_on_invalid_limit_offset(self):
        self.assertEquals(0, self.plugin_service.count(), msg='Database is not empty in beginning')
        self.plugin_service.add(Plugin(name='Plugin', module='Module'))

        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve(offset=-1)
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve(offset='0')
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve(offset='ID')
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve(offset=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve(offset=Tag(id=0))

        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve(limit=-1)
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve(limit='0')
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve(limit='ID')
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve(limit=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve(limit=Tag(id=0))

    def test_plugin_retrieve_by_name_raises_on_invalid_limit_offset(self):
        self.assertEquals(0, self.plugin_service.count(), msg='Database is not empty in beginning')
        db_plugin = self.plugin_service.add(Plugin(name='Plugin', module='Module'))

        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve_by_name(name=db_plugin.name, offset=-1)
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve_by_name(name=db_plugin.name, offset='0')
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve_by_name(name=db_plugin.name, offset='ID')
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve_by_name(name=db_plugin.name, offset=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve_by_name(name=db_plugin.name, offset=Tag(id=0))

        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve_by_name(name=db_plugin.name, limit=-1)
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve_by_name(name=db_plugin.name, limit='0')
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve_by_name(name=db_plugin.name, limit='ID')
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve_by_name(name=db_plugin.name, limit=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve_by_name(name=db_plugin.name, limit=Tag(id=0))

    def test_plugin_retrieve_by_name_raises_on_invalid_name(self):
        self.assertEquals(0, self.plugin_service.count(), msg='Database is not empty in beginning')
        db_plugin = self.plugin_service.add(Plugin(name='Plugin', module='Module'))

        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve_by_name(name=-1)
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve_by_name(name=0)
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve_by_name(name=1)
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve_by_name(name=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve_by_name(name=Tag(id=0))

    def test_plugin_retrieve_offset_limit(self):
        number_of_plugins = 25
        max_fetch = 10
        expected_id_set = set(
            map(lambda o: o.id, self._create_plugins(number_of_plugins)))
        self.assertEquals(number_of_plugins, len(expected_id_set))

        all_retrieved_set = set()
        offset = 0
        while True:
            plugins = self.plugin_service.retrieve(
                offset=offset, limit=max_fetch)
            retrieved_id_set = set(map(lambda o: o.id, (plugins)))
            self.assertTrue(all_retrieved_set.isdisjoint(retrieved_id_set),
                            msg='ids overlap with previously retrieved object'
                            ' when there should be no overlap')
            all_retrieved_set.update(retrieved_id_set)
            if len(plugins) != max_fetch:
                self.assertEquals(number_of_plugins % max_fetch, len(plugins))
                break
            offset += max_fetch
        self.assertEquals(expected_id_set, all_retrieved_set)

    def test_plugin_retrieve_by_name_offset_limit(self):
        number_of_plugins = 25
        max_fetch = 10
        db_plugins = self._create_plugins(number_of_plugins)

        offset = 0
        while True:
            plugins = self.plugin_service.retrieve_by_name(name=db_plugins[0].name,
                                                           offset=offset, limit=max_fetch)
            if len(plugins) != max_fetch:
                break
            offset += max_fetch
        self.assertEquals(len(plugins), 1, 'Returned too many plugins - name should be unique')

        offset = 0
        while True:
            plugins = self.plugin_service.retrieve_by_name(name=db_plugins[number_of_plugins-1].name,
                                                           offset=offset, limit=max_fetch)
            if len(plugins) != max_fetch:
                break
            offset += max_fetch
        self.assertEquals(len(plugins), 1, 'Returned too many plugins - name should be unique')

        offset = 0
        while True:
            plugins = self.plugin_service.retrieve_by_name(name='Unknown name',
                                                           offset=offset, limit=max_fetch)
            if len(plugins) != max_fetch:
                break
            offset += max_fetch
        self.assertEquals(len(plugins), 0, 'Returned too many plugins - name should not exist')

    def test_plugin_retrieve_by_name_regexp(self):
        number_of_plugins = 25
        max_fetch = 10
        self._create_plugins(number_of_plugins)

        offset = 0
        while True:
            plugins = self.plugin_service.retrieve_by_name(name='Plugin*',
                                                           offset=offset, limit=max_fetch)
            if len(plugins) != max_fetch:
                break
            offset += max_fetch
        # This should (if regex works) return number_of_plugins items
        self.assertEquals(len(plugins), 0, 'Returned too many plugins - name should be unique')

    def test_plugin_retrieve_by_id(self):
        number_of_plugins = 25
        db_plugins=self._create_plugins(number_of_plugins)
        ids = range(0, number_of_plugins)
        shuffle(ids)

        for i in range(0, number_of_plugins):
            db_plugin=self.plugin_service.retrieve_by_id(id=db_plugins[ids[i]].id)
            self.assertEquals(db_plugin, db_plugins[ids[i]])
            self.assertEquals(db_plugin.id, db_plugins[ids[i]].id)
            self.assertEquals(db_plugin.name, db_plugins[ids[i]].name)
            self.assertEquals(db_plugin.module, db_plugins[ids[i]].module)

    def test_plugin_retrieve_by_id_raises_on_invalid_id(self):
        self.assertEquals(0, self.plugin_service.count(), msg='Database is not empty in beginning')
        self.plugin_service.add(Plugin(name='Plugin', module='Module'))

        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve_by_id(id=-1)
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve_by_id(id=0)
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve_by_id(id=20000)
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve_by_id(id='0')
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve_by_id(id='ID')
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve_by_id(id=3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.retrieve_by_id(id=Plugin(id=1))

    def test_plugin_add_raises_on_invalid_input(self):
        self.assertEquals(0, self.plugin_service.count(), msg='Database is not empty in beginning')

        with self.assertRaises(ObjectCubeException):
            self.plugin_service.add(None)
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.add(Tag(id=1))
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.add(Plugin())

        # There should be no ID
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.add(Plugin(id=12, name='Plugin', module='Module'))
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.add(Plugin(id='12', name='Plugin', module='Module'))
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.add(Plugin(id=3.1415297, name='Plugin', module='Module'))

        # The name should be a string
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.add(Plugin(name=12, module='Module'))
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.add(Plugin(name=3.1415297, module='Module'))
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.add(Plugin(name=Tag(), module='Module'))

        # The module should be a string
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.add(Plugin(name='Plugin', module=12))
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.add(Plugin(name='Plugin', module=3.1415297))
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.add(Plugin(name='Plugin', module=Tag()))

        self.assertEquals(0, self.plugin_service.count(), msg='Could add invalid plugin')

    def test_plugin_add_raises_on_partial_duplicate(self):
        self.assertEquals(0, self.plugin_service.count(), msg='Database is not empty in beginning')
        self.plugin_service.add(Plugin(name='PluginA', module='ModuleA'))
        self.assertEquals(1, self.plugin_service.count(), msg='Plugin not inserted')

        with self.assertRaises(ObjectCubeException):
            self.plugin_service.add(Plugin(name='PluginA', module='ModuleB'))
        with self.assertRaises(ObjectCubeException):
            self.plugin_service.add(Plugin(name='PluginB', module='ModuleA'))

        self.assertEquals(1, self.plugin_service.count(), msg='Could add partially duplicate plugin')

