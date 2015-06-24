from utils import execute_sql_fetch_single, execute_sql_fetch_multiple
from objectcube.services.base import BasePluginService
from objectcube.exceptions import ObjectCubeException
from objectcube.vo import Plugin
from types import UnicodeType, LongType
from logging import getLogger


class PluginService(BasePluginService):
    def __init__(self):
        super(PluginService, self).__init__()
        self.logger = getLogger('postgreSQL: PluginService')

    def count(self):
        self.logger.debug('count()')
        sql = 'SELECT COUNT(1) AS count ' \
              'FROM PLUGINS'
        return execute_sql_fetch_single(lambda count: count, sql)

    def add(self, plugin):
        self.logger.debug('add(): %s', repr(plugin))

        if not isinstance(plugin, Plugin):
            raise ObjectCubeException('Function requires valid plugin')
        if not plugin.name:
            raise ObjectCubeException('Function requires valid name')
        if not plugin.module:
            raise ObjectCubeException('Function requires valid module')
        if plugin.id:
            raise ObjectCubeException('Function must not get id')

        sql = 'INSERT ' \
              'INTO PLUGINS (NAME, MODULE) ' \
              'VALUES (%s, %s) ' \
              'RETURNING *'
        params = (plugin.name, plugin.module)
        return execute_sql_fetch_single(Plugin, sql, params)

    def retrieve_by_id(self, id_):
        self.logger.debug('retrieve_by_id(): %s', repr(id_))

        if not isinstance(id_, LongType):
            raise ObjectCubeException('Function requires valid id')

        sql = 'SELECT  ID, NAME, MODULE ' \
              'FROM PLUGINS ' \
              'WHERE ID = %s'
        params = (id_,)
        return execute_sql_fetch_single(Plugin, sql, params)

    def retrieve_by_name(self, name):
        self.logger.debug('retrieve_by_name(): %s', repr(name))

        if not isinstance(name, UnicodeType):
            raise ObjectCubeException('Function requires valid name')

        sql = 'SELECT  ID, NAME, MODULE ' \
              'FROM PLUGINS ' \
              'WHERE NAME = %s'
        params = (name, )
        return execute_sql_fetch_single(Plugin, sql, params)

    def retrieve(self, offset=0L, limit=10L):
        self.logger.debug('retrieve(): %s / %s',
                     repr(offset), repr(limit))

        if not isinstance(offset, LongType):
            raise ObjectCubeException('Function requires valid offset')
        if not isinstance(limit, LongType):
            raise ObjectCubeException('Function requires valid limit')

        sql = 'SELECT ID, NAME, MODULE ' \
              'FROM PLUGINS ' \
              'OFFSET %s LIMIT %s'
        params = (offset, limit)
        return execute_sql_fetch_multiple(Plugin, sql, params)

    def retrieve_by_regex(self, name, offset=0L, limit=10L):
        self.logger.debug('retrieve_by_regex(): %s / %s / %s',
                          repr(name), repr(offset), repr(limit))

        if not isinstance(name, UnicodeType):
            raise ObjectCubeException('Function requires valid name regex')
        if not isinstance(offset, LongType):
            raise ObjectCubeException('Function requires valid offset')
        if not isinstance(limit, LongType):
            raise ObjectCubeException('Function requires valid limit')

        sql = 'SELECT  ID, NAME, MODULE ' \
              'FROM PLUGINS ' \
              'WHERE NAME ~ %s ' \
              'OFFSET %s LIMIT %s'
        params = (name, offset, limit)
        return execute_sql_fetch_multiple(Plugin, sql, params)
