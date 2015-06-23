from utils import execute_sql_fetch_single, execute_sql_fetch_multiple
from objectcube.services.base import BasePluginService
from objectcube.exceptions import ObjectCubeException
from objectcube.vo import Plugin
from types import UnicodeType, LongType
import random

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

        if not isinstance(plugin, Plugin):
            raise ObjectCubeException('Function requires valid plugin')
        if plugin.name:
            raise ObjectCubeException('Function requires valid name')
        if plugin.module == '':
            raise ObjectCubeException('Function requires valid module')
#        if plugin.name is None or plugin.name == '':
#            raise ObjectCubeException('Function requires valid name')
#        if plugin.module is None or plugin.module == '':
#            raise ObjectCubeException('Function requires valid module')
        if plugin.id:
            raise ObjectCubeException('Function must not get id')

        sql = 'INSERT ' \
              'INTO PLUGINS (NAME, MODULE) ' \
              'VALUES (%s, %s) ' \
              'RETURNING *'
        params = (plugin.name, plugin.module)
        return execute_sql_fetch_single(Plugin, sql, params)

    def retrieve_by_id(self, id):
        logger.debug('retrieve_by_id(): %s', repr(id))

        if id is None or not isinstance(id, LongType):
            raise ObjectCubeException('Function requires valid id')

        sql = 'SELECT  ID, NAME, MODULE ' \
              'FROM PLUGINS ' \
              'WHERE ID = %s'
        params = (id,)
        return execute_sql_fetch_single(Plugin, sql, params)

    def retrieve_by_name(self, name):
        logger.debug('retrieve_by_name(): %s', repr(name))

        if name is None or not isinstance(name, UnicodeType):
            raise ObjectCubeException('Function requires valid name')

        sql = 'SELECT  ID, NAME, MODULE ' \
              'FROM PLUGINS ' \
              'WHERE NAME = %s'
        params = (name, )
        return execute_sql_fetch_single(Plugin, sql, params)

    def retrieve(self, offset=0, limit=10):
        logger.debug('retrieve(): %s / %s',
                     repr(offset), repr(limit))

        if offset is None or not isinstance(offset, LongType):
            raise ObjectCubeException('Function requires valid offset')
        if limit is None or not isinstance(limit, LongType):
            raise ObjectCubeException('Function requires valid limit')

        sql = 'SELECT ID, NAME, MODULE ' \
              'FROM PLUGINS ' \
              'OFFSET %s LIMIT %s'
        params = (offset, limit)
        return execute_sql_fetch_multiple(Plugin, sql, params)

    def retrieve_by_regex(self, regex, offset=0, limit=10):
        logger.debug('retrieve_by_regex(): %s / %s / %s',
                     repr(regex), repr(offset), repr(limit))

        if regex is None or not isinstance(regex, UnicodeType):
            raise ObjectCubeException('Function requires valid regex')
        if offset is None or not isinstance(offset, LongType):
            raise ObjectCubeException('Function requires valid offset')
        if limit is None or not isinstance(limit, LongType):
            raise ObjectCubeException('Function requires valid limit')

        sql = 'SELECT  ID, NAME, MODULE ' \
              'FROM PLUGINS ' \
              'WHERE NAME ~ %s ' \
              'OFFSET %s LIMIT %s'
        params = (regex, offset, limit)
        return execute_sql_fetch_multiple(Plugin, sql, params)
