from utils import execute_sql_fetch_single, execute_sql_fetch_multiple
from objectcube.services.base import BaseObjectService
from objectcube.exceptions import ObjectCubeException
from objectcube.vo import Object, Tag
from types import IntType, LongType, StringTypes

import logging
logger = logging.getLogger('postgreSQL: ObjectService')

class ObjectService(BaseObjectService):
    def __init__(self):
        super(ObjectService, self).__init__()

    def count(self):
        logger.debug('count()')
        sql = 'SELECT COUNT(1) AS count ' \
              'FROM OBJECTS'
        return execute_sql_fetch_single(lambda count: count, sql)

    def add(self, obj):
        logger.debug('add(): %s', repr(obj))

        if obj is None or not isinstance(obj, Object):
            raise ObjectCubeException('Function requires valid Object')
        if not obj.name or \
                not isinstance(obj.name, StringTypes) or obj.name == '':
            raise ObjectCubeException('Function requires valid name')
        if not obj.digest or \
                not isinstance(obj.digest, StringTypes) or obj.digest == '':
            raise ObjectCubeException('Function requires valid digest')
        if obj.id is not None:
            raise ObjectCubeException('Function must not get id')

        sql = 'INSERT ' \
              'INTO OBJECTS (NAME, DIGEST) ' \
              'VALUES (%s, %s) ' \
              'RETURNING *'
        params = (obj.name, obj.digest)
        return execute_sql_fetch_single(Object, sql, params)

    def update(self, obj):
        logger.debug('update(): %s', repr(obj))

        if obj is None or not isinstance(obj, Object):
            raise ObjectCubeException('Function requires valid Object')
        if obj.id is None or not isinstance(obj.id, IntType):
            raise ObjectCubeException('Function requires valid id')
        if not obj.name or \
                not isinstance(obj.name, StringTypes) or obj.name == '':
            raise ObjectCubeException('Function requires valid name')
        if not obj.digest or \
                not isinstance(obj.digest, StringTypes) or obj.digest == '':
            raise ObjectCubeException('Function requires valid digest')

        sql = 'UPDATE OBJECTS ' \
              'SET NAME = %s, DIGEST = %s ' \
              'WHERE ID = %s ' \
              'RETURNING *'
        params = (obj.name, obj.digest, obj.id)
        db_object = execute_sql_fetch_single(Object, sql, params)

        if db_object is None:
            raise ObjectCubeException('No Object found to update')
        return db_object

    def delete(self, obj):
        logger.debug('delete(): %s', repr(obj))

        if obj is None or not isinstance(obj, Object):
            raise ObjectCubeException('Function requires valid Object')
        if obj.id is None or not isinstance(obj.id, IntType):
            raise ObjectCubeException('Function requires valid id')

        sql = 'DELETE ' \
              'FROM OBJECTS ' \
              'WHERE ID = %s ' \
              'RETURNING *'
        params = (obj.id, )
        db_object = execute_sql_fetch_single(Object, sql, params)

        if db_object is None:
            raise ObjectCubeException('No Object found to delete')
        return None

    def delete_by_id(self, id):
        logger.debug('delete_by_id(): %s', repr(id))

        if id is None or not isinstance(id, IntType):
            raise ObjectCubeException('Function requires valid id')

        sql = 'DELETE ' \
              'FROM OBJECTS ' \
              'WHERE ID = %s ' \
              'RETURNING *'
        params = (id, )
        db_object = execute_sql_fetch_single(Object, sql, params)

        if db_object is None:
            raise ObjectCubeException('No Object found to delete')
        return None

    def retrieve_by_id(self, id):
        logger.debug('retrieve_by_id(): %s', repr(id))

        if id is None or not isinstance(id, IntType):
            raise ObjectCubeException('Function requires valid id')

        sql = "SELECT * " \
              "FROM OBJECTS " \
              "WHERE ID = %s"
        params = (id,)
        return execute_sql_fetch_single(Object, sql, params)

    def retrieve(self, offset=0, limit=10):
        logger.debug('retrieve(): %s / %s',
                     repr(offset), repr(limit))

        if offset is None or not isinstance(offset, (IntType, LongType)):
            raise ObjectCubeException('Function requires valid offset')
        if limit is None or not isinstance(limit, (IntType, LongType)):
            raise ObjectCubeException('Function requires valid limit')

        sql = 'SELECT ID, NAME, DIGEST ' \
              'FROM OBJECTS ' \
              'OFFSET %s LIMIT %s'
        params = (offset, limit)
        return execute_sql_fetch_multiple(Object, sql, params)

    def retrieve_by_regex(self, name, offset=0, limit=10):
        logger.debug('retrieve_by_regex(): %s / %s / %s',
                     repr(name), repr(offset), repr(limit))

        if name is None or not isinstance(name, StringTypes):
            raise ObjectCubeException('Function requires valid name regex')
        if offset is None or not isinstance(offset, (IntType, LongType)):
            raise ObjectCubeException('Function requires valid offset')
        if limit is None or not isinstance(limit, (IntType, LongType)):
            raise ObjectCubeException('Function requires valid limit')

        sql = 'SELECT ID, NAME, DIGEST ' \
              'FROM OBJECTS ' \
              'WHERE NAME ~ %s ' \
              'OFFSET %s LIMIT %s'
        params = (name, offset, limit)
        return execute_sql_fetch_multiple(Object, sql, params)

    def retrieve_by_tag(self, tag, offset=0, limit=10):
        logger.debug('retrieve_by_tag(): %s / %s / %s',
                     repr(tag), repr(offset), repr(limit))

        if tag is None or not isinstance(tag, Tag):
            raise ObjectCubeException('Function requires valid tag')
        if tag.id is None or not isinstance(tag.id, IntType):
            raise ObjectCubeException('Function requires valid tag id')
        if offset is None or not isinstance(offset, (IntType, LongType)):
            raise ObjectCubeException('Function requires valid offset')
        if limit is None or not isinstance(limit, (IntType, LongType)):
            raise ObjectCubeException('Function requires valid limit')

        sql = 'SELECT O.ID, O.NAME, O.DIGEST ' \
              'FROM OBJECTS O JOIN TAGGINGS T ON O.ID = T.OBJECT_ID ' \
              'WHERE T.TAG_ID = %s ' \
              'OFFSET %s LIMIT %s'
        params = (tag.id, offset, limit)
        return execute_sql_fetch_multiple(Object, sql, params)

