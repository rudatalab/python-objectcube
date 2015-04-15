from utils import execute_single_sql
from objectcube.services.base import BasePluginService
from objectcube.vo import Plugin


class PluginService(BasePluginService):

    def count(self):
        pass

    def get_plugin_by_name(self):
        pass

    def add(self, plugin):
        if plugin.id:
            raise ObjectCubeException('Unable to to add plugin that has id')

        sql = 'INSERT INTO PLUGINS(NAME, MODULE) ' \
              'VALUES(%s, %s) RETURNING *'
        params = (plugin.name, plugin.module)

        return execute_single_sql(Plugin, sql, params)

    def get_plugin_by_id(self):
        pass

    def get_plugins(self):
        pass

    def process(self, _object, _data):
        pass
