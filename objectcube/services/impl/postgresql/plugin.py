from utils import execute_sql_fetch_single, execute_sql_fetch_multiple
from objectcube.services.base import BasePluginService
from objectcube.exceptions import ObjectCubeException
from objectcube.vo import Plugin
from types import StringType, IntType

import logging
logger = logging.getLogger('postgreSQL: PluginService')

class PluginService(BasePluginService):
    def __init__(self):
        super(PluginService, self).__init__()

    def count(self):
        logger.debug('count()')
        sql = 'SELECT COUNT(1) AS count ' \
              'FROM PLUGINS'
        return execute_sql_fetch_single(lambda count: count, sql)

    def add(self, plugin):
        logger.debug('add(): %s', repr(plugin))

        if plugin is None or not isinstance(plugin, Plugin):
            raise ObjectCubeException('Must give a valid plugin')
        if plugin.name is None or not isinstance(plugin.name, StringType) or plugin.name == '':
            raise ObjectCubeException('Must give plugin with valid name')
        if plugin.module is None or not isinstance(plugin.module, StringType) or plugin.module == '':
            raise ObjectCubeException('Must give plugin with valid module')
        if not plugin.id is None:
            raise ObjectCubeException('Must give plugin without valid id')

        sql = 'INSERT ' \
              'INTO PLUGINS (NAME, MODULE) ' \
              'VALUES (%s, %s) ' \
              'RETURNING *'
        params = (plugin.name, plugin.module)
        return execute_sql_fetch_single(Plugin, sql, params)

    def retrieve(self, offset=0, limit=10):
        logger.debug('retrieve(): %s / %s', repr(offset), repr(limit))

        if offset is None or not isinstance(offset, IntType):
            raise ObjectCubeException('Must give valid offset')
        if limit is None or not isinstance(limit, IntType):
            raise ObjectCubeException('Must give valid limit')

        sql = 'SELECT ID, NAME, MODULE ' \
              'FROM PLUGINS ' \
              'OFFSET %s LIMIT %s'
        params = (offset, limit)
        return execute_sql_fetch_multiple(Plugin, sql, params)

    def retrieve_by_id(self, id):
        logger.debug('retrieve_by_id(): %s', repr(id))

        if id is None or not isinstance(id, IntType):
            raise ObjectCubeException('Must give valid object id')

        sql = 'SELECT  ID, NAME, MODULE ' \
              'FROM PLUGINS ' \
              'WHERE ID = %s'
        params = (id,)
        db_plugin = execute_sql_fetch_single(Plugin, sql, params)

        if db_plugin is None:
            raise ObjectCubeException('No Plugin found with id {}'.format(id))
        return db_plugin


    def retrieve_by_name(self, name, offset=0, limit=10):
        logger.debug('retrieve_by_name(): %s / %s / %s', repr(name), repr(offset), repr(limit))

        if name is None or not isinstance(name, StringType):
            raise ObjectCubeException('Must give valid name')
        if offset is None or not isinstance(offset, IntType):
            raise ObjectCubeException('Must give valid offset')
        if limit is None or not isinstance(limit, IntType):
            raise ObjectCubeException('Must give valid limit')

        sql = 'SELECT  ID, NAME, MODULE ' \
              'FROM PLUGINS ' \
              'WHERE NAME = %s ' \
              'OFFSET %s LIMIT %s'
        params = (name, offset, limit)
        return execute_sql_fetch_multiple(Plugin, sql, params)
