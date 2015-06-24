from utils import *
from objectcube.services.base import BaseTaggingService
from objectcube.exceptions import ObjectCubeException
from objectcube.data_objects import Object, Plugin, Tag, Tagging
from types import LongType, UnicodeType

import logging
logger = logging.getLogger('postgreSQL: TaggingService')

class TaggingService(BaseTaggingService):

    def count(self):
        logger.debug('count()')
        sql = 'SELECT COUNT(1) AS count ' \
              'FROM TAGGINGS'
        return execute_sql_fetch_single(lambda count: count, sql)

    def add(self, tag, object_, meta, plugin=None, plugin_set_id=None):
        logger.debug('add(): %s / %s / %s / %s / %s',
                     repr(tag), repr(object_), repr(meta),
                     repr(plugin), repr(plugin_set_id))

        if not isinstance(tag, Tag):
            raise ObjectCubeException('Must give valid tag')
        if not isinstance(object_, Object):
            raise ObjectCubeException('Must give valid object')
        if meta is not None \
                and not isinstance(meta, unicode):
            raise ObjectCubeException('If given, meta must be valid')
        if plugin is not None \
                and (not isinstance(plugin, Plugin)
                     or not isinstance(plugin.id, LongType)):
            raise ObjectCubeException('If given, plugin must be a valid Plugin')
        if plugin_set_id is not None \
                and not isinstance(plugin_set_id, LongType):
            raise ObjectCubeException('If given, plugin_set_id must be valid')

        sql_attributes = 'OBJECT_ID, TAG_ID'
        sql_values = '%s, %s'
        params = (object_.id, tag.id)

        if meta is not None:
            sql_attributes += ', META'
            sql_values += ',%s'
            params += (meta,)

        if plugin is not None:
            sql_attributes += ', PLUGIN_ID'
            sql_values += ',%s'
            params += (plugin.id,)

        if plugin_set_id is not None:
            sql_attributes += ', PLUGIN_SET_ID'
            sql_values += ',%s'
            params += (plugin_set_id,)

        sql = 'INSERT INTO TAGGINGS (' + \
              sql_attributes + \
              ') VALUES (' \
              + sql_values + \
              ') RETURNING *'
        return execute_sql_fetch_single(Tagging, sql, params)

    def delete_by_set_id(self, plugin_set_id):
        logger.debug('delete_by_set_id(): %s', repr(plugin_set_id))

        if plugin_set_id is None or not isinstance(plugin_set_id, LongType):
            raise ObjectCubeException('Must give valid plugin_set_id')

        sql = 'DELETE ' \
              'FROM TAGGINGS ' \
              'WHERE PLUGIN_SET_ID = %s ' \
              'RETURNING *'
        params = (plugin_set_id, )
        execute_sql_fetch_single(Tagging, sql, params)
        return None

    def resolve(self, tag, object, meta, plugin, plugin_set_id):
        logger.debug('resolve(): %s / %s / %s / %s / %s',
                     repr(tag), repr(object), repr(meta), repr(plugin), repr(plugin_set_id))

        if plugin_set_id is None or not isinstance(plugin_set_id, LongType):
            raise ObjectCubeException('Must give valid plugin_set_id to merge')

        tagging = self.add(tag, object, meta, plugin, plugin_set_id)
        sql = 'DELETE ' \
              'FROM TAGGINGS ' \
              'WHERE PLUGIN_SET_ID = %s ' \
              '  AND NOT ID = %s ' \
              'RETURNING *'
        params = (plugin_set_id, tagging.id)
        execute_sql_fetch_single(Tagging, sql, params)
        return tag

    def delete(self, tagging):
        logger.debug('delete(): %s', repr(tagging))

        if tagging is None or not isinstance(tagging, Tagging) or \
                tagging.id is None or not isinstance(tagging.id, LongType):
            raise ObjectCubeException('Must give tagging with valid id')

        sql = 'DELETE FROM TAGGINGS ' \
              'WHERE ID = %s' \
              'RETURNING *'
        params = (tagging.id, )
        execute_sql_fetch_single(Tagging, sql, params)
        return None

    def retrieve_by_id(self, tagging_id):
        logger.debug('retrieve_by_id(): %s', repr(tagging_id))

        if tagging_id is None or tagging_id <= 0 or not isinstance(tagging_id, LongType):
            raise ObjectCubeException('Id value must be a positive number')

        sql = 'SELECT * ' \
              'FROM TAGGINGS ' \
              'WHERE ID = %s'
        params = (tagging_id,)
        return execute_sql_fetch_single(Tagging, sql, params)

    def retrieve_by_tag_id(self, tag_id, offset=0, limit=10):
        logger.debug('retrieve_by_tag_id(): %s', repr(tag_id))

        if tag_id is None or not isinstance(tag_id, LongType):
            raise ObjectCubeException('Must give valid tag id')

        sql = 'SELECT * ' \
              'FROM TAGGINGS ' \
              'WHERE TAG_ID = %s ' \
              'OFFSET %s LIMIT %s'
        params = (tag_id, offset, limit)
        return execute_sql_fetch_multiple(Tagging, sql, params)

    def retrieve_by_object_id(self, object_id, offset=0, limit=10):
        logger.debug('retrieve_by_object_id(): %s', repr(object_id))

        if object_id is None or not isinstance(object_id, LongType):
            raise ObjectCubeException('Must give valid object id')

        sql = 'SELECT * ' \
              'FROM TAGGINGS ' \
              'WHERE OBJECT_ID = %s ' \
              'OFFSET %s LIMIT %s'
        params = (object_id, offset, limit)
        return execute_sql_fetch_multiple(Tagging, sql, params)

    def retrieve_by_set_id(self, plugin_set_id, offset=0, limit=10):
        logger.debug('retrieve_by_set_id(): %s', repr(plugin_set_id))

        if not plugin_set_id or not isinstance(plugin_set_id, LongType):
            raise ObjectCubeException('Must give valid plugin set id')

        sql = 'SELECT * ' \
              'FROM TAGGINGS ' \
              'WHERE PLUGIN_SET_ID = %s ' \
              'OFFSET %s LIMIT %s'
        params = (plugin_set_id, offset, limit)
        return execute_sql_fetch_multiple(Tagging, sql, params)

    def update(self, tagging):
        logger.debug('update(): %s', repr(tagging))

        if tagging is None or not isinstance(tagging, Tagging):
            raise ObjectCubeException('Must give valid tagging')
        if tagging.id is None or not isinstance(tagging.id, LongType):
            raise ObjectCubeException('Must give tagging with valid id')
        if not tagging.meta is None and not isinstance(tagging.meta, UnicodeType):
            raise ObjectCubeException('If given, meta must be valid string')

        if tagging.meta is None:
            sql = 'UPDATE TAGGINGS ' \
                  'SET META = NULL ' \
                  'WHERE ID = %s ' \
                  'RETURNING *'
            params = (tagging.id,)
        else:
            sql = 'UPDATE TAGGINGS ' \
                  'SET META = %s ' \
                  'WHERE ID = %s ' \
                  'RETURNING *'
            params = (tagging.meta, tagging.id)
        return execute_sql_fetch_single(Tagging, sql, params)
