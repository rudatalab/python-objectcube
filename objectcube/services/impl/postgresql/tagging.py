from utils import execute_sql_fetch_single, execute_sql_fetch_multiple
from objectcube.services.base import BaseTaggingService
from objectcube.exceptions import ObjectCubeException
from objectcube.data_objects import Tagging
from types import LongType
from logging import getLogger


class TaggingService(BaseTaggingService):
    def __init__(self):
        super(TaggingService, self).__init__()
        self.logger = getLogger('postgreSQL: TaggingService')

    def count(self):
        self.logger.debug('count()')
        sql = 'SELECT COUNT(1) AS count ' \
              'FROM TAGGINGS'
        return execute_sql_fetch_single(lambda count: count, sql)

    def add(self, tagging):
        self.logger.debug('add(): %s ', repr(tagging))

        if not isinstance(tagging, Tagging):
            raise ObjectCubeException('Function requires valid tagging')
        if tagging.id is not None:
            raise ObjectCubeException('Function must not get Tagging id')
        if tagging.plugin_set_id and not tagging.plugin_id:
            raise ObjectCubeException('Cannot have plugin set w/o plugin')

        # Build the SQL expression, starting with required attributes
        sql_attributes = 'TAG_ID, OBJECT_ID'
        sql_values = '%s, %s'
        params = (tagging.tag_id, tagging.object_id)

        # Build the SQL expression, continuing with optional attributes
        if tagging.meta:
            sql_attributes += ', META'
            sql_values += ', %s'
            params += (tagging.meta,)
        if tagging.plugin_id:
            sql_attributes += ', PLUGIN_ID'
            sql_values += ',%s'
            params += (tagging.plugin_id,)
        if tagging.plugin_set_id:
            sql_attributes += ', PLUGIN_SET_ID'
            sql_values += ',%s'
            params += (tagging.plugin_set_id,)

        sql = 'INSERT INTO TAGGINGS (' + \
              sql_attributes + \
              ') VALUES (' \
              + sql_values + \
              ') RETURNING *'
        return execute_sql_fetch_single(Tagging, sql, params)

    def update(self, tagging):
        self.logger.debug('update(): %s', repr(tagging))

        if not isinstance(tagging, Tagging):
            raise ObjectCubeException('Function requires valid tagging')
        if not tagging.id:
            raise ObjectCubeException('Function requires valid id')

        # Get the old tag to verify that it exists,
        # and then run some business logic checks
        old = self.retrieve_by_id(tagging.id)
        if not old:
            raise ObjectCubeException('No Tag found to update')
        if tagging.tag_id != old.tag_id \
                or tagging.object_id != old.object_id \
                or tagging.plugin_id != old.plugin_id \
                or tagging.plugin_set_id != old.plugin_set_id:
            raise ObjectCubeException('Can only update meta')

        if tagging.meta:
            sql = 'UPDATE TAGGINGS ' \
                  'SET META = %s ' \
                  'WHERE ID = %s ' \
                  'RETURNING *'
            params = (tagging.meta, tagging.id)
        else:
            sql = 'UPDATE TAGGINGS ' \
                  'SET META = NULL ' \
                  'WHERE ID = %s ' \
                  'RETURNING *'
            params = (tagging.id,)
        return execute_sql_fetch_single(Tagging, sql, params)

    def resolve(self, tagging):
        self.logger.debug('resolve(): %s', repr(tagging))

        if not isinstance(tagging, Tagging):
            raise ObjectCubeException('Function requires valid Tagging')
        if not tagging.plugin_set_id:
            raise ObjectCubeException('Function requires valid plugin set id')

        if tagging.id:
            db_tagging = self.update(tagging)
        else:
            db_tagging = self.add(tagging)

        # Delete all the other ones in the set
        # It is possible that this deletes nothing, which is OK
        # This could happen, for example, when confirming a tagging
        # without alternatives
        sql = 'DELETE ' \
              'FROM TAGGINGS ' \
              'WHERE PLUGIN_SET_ID = %s ' \
              '  AND NOT ID = %s ' \
              'RETURNING *'
        params = (db_tagging.plugin_set_id, db_tagging.id)
        execute_sql_fetch_single(Tagging, sql, params)
        return db_tagging

    def delete(self, tagging):
        self.logger.debug('delete(): %s', repr(tagging))

        if not isinstance(tagging, Tagging):
            raise ObjectCubeException('Function requires valid Tagging')
        if not tagging.id:
            raise ObjectCubeException('Function requires valid id')

        sql = 'DELETE FROM TAGGINGS ' \
              'WHERE ID = %s' \
              'RETURNING *'
        params = (tagging.id, )
        db_tagging = execute_sql_fetch_single(Tagging, sql, params)

        if not db_tagging:
            raise ObjectCubeException('No Tagging found to delete')
        return None

    def delete_by_id(self, id_):
        self.logger.debug('delete_by_id(): %s', repr(id_))

        if not isinstance(id_, LongType):
            raise ObjectCubeException('Function requires valid id')

        sql = 'DELETE FROM TAGGINGS ' \
              'WHERE ID = %s' \
              'RETURNING *'
        params = (id_, )
        db_tagging = execute_sql_fetch_single(Tagging, sql, params)

        if not db_tagging:
            raise ObjectCubeException('No Tagging found to delete')
        return None

    def delete_by_set_id(self, plugin_set_id):
        self.logger.debug('delete_by_set_id(): %s', repr(plugin_set_id))

        if not isinstance(plugin_set_id, LongType):
            raise ObjectCubeException('Function requires valid plugin set id')

        sql = 'DELETE ' \
              'FROM TAGGINGS ' \
              'WHERE PLUGIN_SET_ID = %s ' \
              'RETURNING *'
        params = (plugin_set_id, )
        db_tagging = execute_sql_fetch_single(Tagging, sql, params)

        if not db_tagging:
            raise ObjectCubeException('No Tagging found to delete')
        return None

    def retrieve_by_id(self, id_):
        self.logger.debug('retrieve_by_id(): %s', repr(id_))

        if not isinstance(id_, LongType):
            raise ObjectCubeException('Function requires valid id')

        sql = 'SELECT * ' \
              'FROM TAGGINGS ' \
              'WHERE ID = %s'
        params = (id_,)
        return execute_sql_fetch_single(Tagging, sql, params)

    def retrieve(self, offset=0L, limit=10L):
        self.logger.debug('retrieve(): %s / %s',
                          repr(offset), repr(limit))

        if not isinstance(offset, LongType):
            raise ObjectCubeException('Function requires valid offset')
        if not isinstance(limit, LongType):
            raise ObjectCubeException('Function requires valid limit')

        sql = 'SELECT * ' \
              'FROM TAGGINGS ' \
              'OFFSET %s LIMIT %s'
        params = (offset, limit)
        return execute_sql_fetch_multiple(Tagging, sql, params)

    def retrieve_by_tag_id(self, tag_id, offset=0L, limit=10L):
        self.logger.debug('retrieve_by_tag_id(): %s', repr(tag_id))

        if not isinstance(tag_id, LongType):
            raise ObjectCubeException('Function requires valid tag id')

        if not isinstance(offset, LongType):
            raise ObjectCubeException('Function requires valid offset')
        if not isinstance(limit, LongType):
            raise ObjectCubeException('Function requires valid limit')

        sql = 'SELECT * ' \
              'FROM TAGGINGS ' \
              'WHERE TAG_ID = %s ' \
              'OFFSET %s LIMIT %s'
        params = (tag_id, offset, limit)
        return execute_sql_fetch_multiple(Tagging, sql, params)

    def retrieve_by_object_id(self, object_id, offset=0L, limit=10L):
        self.logger.debug('retrieve_by_object_id(): %s', repr(object_id))

        if not isinstance(object_id, LongType):
            raise ObjectCubeException('Function requires valid object id')

        if not isinstance(offset, LongType):
            raise ObjectCubeException('Function requires valid offset')
        if not isinstance(limit, LongType):
            raise ObjectCubeException('Function requires valid limit')

        sql = 'SELECT * ' \
              'FROM TAGGINGS ' \
              'WHERE OBJECT_ID = %s ' \
              'OFFSET %s LIMIT %s'
        params = (object_id, offset, limit)
        return execute_sql_fetch_multiple(Tagging, sql, params)

    def retrieve_by_set_id(self, plugin_set_id, offset=0L, limit=10L):
        self.logger.debug('retrieve_by_set_id(): %s', repr(plugin_set_id))

        if not isinstance(plugin_set_id, LongType):
            raise ObjectCubeException('Function requires valid plugin set id')

        if not isinstance(offset, LongType):
            raise ObjectCubeException('Function requires valid offset')
        if not isinstance(limit, LongType):
            raise ObjectCubeException('Function requires valid limit')

        sql = 'SELECT * ' \
              'FROM TAGGINGS ' \
              'WHERE PLUGIN_SET_ID = %s ' \
              'OFFSET %s LIMIT %s'
        params = (plugin_set_id, offset, limit)
        return execute_sql_fetch_multiple(Tagging, sql, params)
