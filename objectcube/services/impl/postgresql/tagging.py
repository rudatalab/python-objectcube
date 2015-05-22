from psycopg2.extras import NamedTupleCursor

from utils import *
from objectcube.services.base import BaseTaggingService
from objectcube.contexts import Connection
from objectcube.vo import Object, Plugin, Tag, Tagging
from objectcube.exceptions import ObjectCubeException
from types import IntType, StringType


class TaggingService(BaseTaggingService):

    def count(self):
        sql = 'SELECT COUNT(1) AS count ' \
              'FROM TAGGING'

        def extract_count(count):
            return count

        return execute_sql_fetch_single(extract_count, sql)

    def add(self, tag, object, meta, plugin=None, plugin_set_id=None):
        if tag is None or not isinstance(tag, Tag) \
                or tag.id is None or not isinstance(tag.id, IntType):
            raise ObjectCubeException('Must give tag with valid id')
        if object is None or not isinstance(object, Object) \
                or object.id is None or not isinstance(object.id, IntType):
            raise ObjectCubeException('Must give object with valid id')
        if not meta is None and not isinstance(meta, StringType):
            raise ObjectCubeException('If given, meta must be a valid string')
        if not plugin is None:
            if not isinstance(plugin, Plugin) or plugin.id is None or not isinstance(plugin.id, IntType):
                raise ObjectCubeException('If given, plugin must be a valid Plugin')
        if not plugin_set_id is None and not isinstance(plugin_set_id, IntType):
            raise ObjectCubeException('If given, plugin_set_id must be valid')

        sql_attributes = 'OBJECT_ID, TAG_ID'
        sql_values = '%s, %s'
        params = (object.id, tag.id)

        if not meta is None:
            sql_attributes += ', META'
            sql_values += ',%s'
            params += (meta,)

        if not plugin is None:
            sql_attributes += ', PLUGIN_ID'
            sql_values += ',%s'
            params += (plugin.id,)

        if not plugin_set_id is None:
            sql_attributes += ', PLUGIN_SET_ID'
            sql_values += ',%s'
            params += (plugin_set_id,)

        sql = 'INSERT INTO TAGGING(' + \
              sql_attributes + \
              ') VALUES (' \
              + sql_values + \
              ') RETURNING *'
        return execute_sql_fetch_single(Tagging, sql, params)

    def delete_by_set_id(self, plugin_set_id):
        if plugin_set_id is None or not isinstance(plugin_set_id, IntType):
            raise ObjectCubeException('Must give valid plugin_set_id')

        sql = 'DELETE ' \
              'FROM TAGGING ' \
              'WHERE PLUGIN_SET_ID = %s ' \
              'RETURNING *'
        params = (plugin_set_id, )
        execute_sql_fetch_single(Tagging, sql, params)
        return None

    def resolve(self, tag, object, meta, plugin, plugin_set_id):
        if plugin_set_id is None or not isinstance(plugin_set_id, IntType):
            raise ObjectCubeException('Must give valid plugin_set_id to merge')

        tagging = self.add(tag, object, meta, plugin, plugin_set_id)
        sql = 'DELETE ' \
              'FROM TAGGING ' \
              'WHERE PLUGIN_SET_ID = %s ' \
              '  AND NOT ID = %s ' \
              'RETURNING *'
        params = (plugin_set_id, tagging.id)
        execute_sql_fetch_single(Tagging, sql, params)
        return tag

    def delete(self, tagging):
        if tagging is None or not isinstance(tagging, Tagging) or \
                tagging.id is None or not isinstance(tagging.id, IntType):
            raise ObjectCubeException('Must give tagging with valid id')

        sql = 'DELETE FROM TAGGING ' \
              'WHERE ID = %s' \
              'RETURNING *'
        params = (tagging.id, )
        execute_sql_fetch_single(Tagging, sql, params)
        return None

    def retrieve_by_id(self, tagging_id):
        if tagging_id is None or tagging_id <= 0 or not isinstance(tagging_id, IntType):
            raise ObjectCubeException('Id value must be a positive number')

        sql = 'SELECT * ' \
              'FROM TAGGING ' \
              'WHERE ID = %s'
        params = (tagging_id,)
        return execute_sql_fetch_single(Tagging, sql, params)

    def retrieve_by_tag_id(self, tag_id, offset=0, limit=10):
        if tag_id is None or not isinstance(tag_id, IntType):
            raise ObjectCubeException('Must give valid tag id')

        sql = "SELECT * " \
              "FROM TAGGING " \
              "WHERE TAG_ID = %s " \
              "OFFSET %s LIMIT %s"
        params = (tag_id, offset, limit)
        return execute_sql_fetch_multiple(Tagging, sql, params)

    def retrieve_by_object_id(self, object_id, offset=0, limit=10):
        if object_id is None or not isinstance(object_id, IntType):
            raise ObjectCubeException('Must give valid object id')

        sql = "SELECT * " \
              "FROM TAGGING " \
              "WHERE OBJECT_ID = %s " \
              "OFFSET %s LIMIT %s"
        params = (object_id, offset, limit)
        return execute_sql_fetch_multiple(Tagging, sql, params)

    def retrieve_by_set_id(self, plugin_set_id, offset=0, limit=10):
        if not plugin_set_id or not isinstance(plugin_set_id, IntType):
            raise ObjectCubeException('Must give valid plugin set id')

        sql = "SELECT * " \
              "FROM TAGGING " \
              "WHERE PLUGIN_SET_ID = %s " \
              "OFFSET %s LIMIT %s"
        params = (plugin_set_id, offset, limit)
        return execute_sql_fetch_multiple(Tagging, sql, params)

    def update(self, tagging):
        if tagging is None or not isinstance(tagging, Tagging):
            raise ObjectCubeException('Must give valid tagging')
        if tagging.id is None or not isinstance(tagging.id, IntType):
            raise ObjectCubeException('Must give tagging with valid id')
        if not tagging.meta is None and not isinstance(tagging.meta, StringType):
            raise ObjectCubeException('If given, meta must be valid string')

        if tagging.meta is None:
            sql = 'UPDATE TAGGING ' \
                  'SET META = NULL ' \
                  'WHERE ID = %s ' \
                  'RETURNING *'
            params = (tagging.id,)
        else:
            sql = 'UPDATE TAGGING ' \
                  'SET META = %s ' \
                  'WHERE ID = %s ' \
                  'RETURNING *'
            params = (tagging.meta, tagging.id)
        return execute_sql_fetch_single(Tagging, sql, params)
