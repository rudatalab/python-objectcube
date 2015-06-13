from utils import execute_sql_fetch_single, execute_sql_fetch_multiple
from objectcube.services.base import BaseObjectService
from objectcube.exceptions import ObjectCubeException
from objectcube.vo import Object, Tag
from types import StringType, IntType

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

    def add(self, object):
        logger.debug('add(): %s', repr(object))

        if object is None or not isinstance(object, Object):
            raise ObjectCubeException('Must give valid object')
        if object.name is None or not isinstance(object.name, StringType) or object.name == '':
            raise ObjectCubeException('Must give object with valid name')
        if object.digest is None or not isinstance(object.digest, StringType) or object.digest == '':
            raise ObjectCubeException('Must give object with valid digest')
        if not object.id is None:
            raise ObjectCubeException('Must give object without valid id')

        sql = 'INSERT ' \
              'INTO OBJECTS (NAME, DIGEST) ' \
              'VALUES (%s, %s) ' \
              'RETURNING *'
        params = (object.name, object.digest)
        return execute_sql_fetch_single(Object, sql, params)

    def retrieve_by_id(self, id):
        logger.debug('retrieve_by_id(): %s', repr(id))

        if id is None or not isinstance(id, IntType):
            raise ObjectCubeException('Must give valid object id')

        sql = "SELECT * " \
              "FROM OBJECTS " \
              "WHERE ID = %s"
        params = (id,)
        return execute_sql_fetch_single(Object, sql, params)

    def retrieve(self, offset=0, limit=10):
        logger.debug('retrieve()')

        sql = 'SELECT ID, NAME, DIGEST ' \
              'FROM OBJECTS ' \
              'OFFSET %s LIMIT %s'
        params = (offset, limit)
        return execute_sql_fetch_multiple(Object, sql, params)

    def retrieve_by_tag(self, tag, offset=0, limit=10):
        logger.debug('retrieve_by_tag(): %s', repr(tag))

        if tag is None or not isinstance(tag, Tag):
            raise ObjectCubeException('Must give valid tag')
        if tag.id is None or not isinstance(tag.id, IntType):
            raise ObjectCubeException('Must give tag with valid id')

        sql = 'SELECT O.ID, O.NAME, O.DIGEST ' \
              'FROM OBJECTS O JOIN TAGGINGS T ON O.ID = T.OBJECT_ID ' \
              'WHERE T.TAG_ID = %s ' \
              'OFFSET %s LIMIT %s'
        params = (tag.id, offset, limit)
        return execute_sql_fetch_multiple(Object, sql, params)

    def update(self, object):
        logger.debug('update(): %s', repr(object))

        if object is None or not isinstance(object, Object):
            raise ObjectCubeException('Unable to update invalid Object')
        if object.id is None or not isinstance(object.id, IntType):
            raise ObjectCubeException('Unable to update Object without id')
        if not object.name or not isinstance(object.name, StringType):
            raise ObjectCubeException('Unable to update Object without a valid name')
        if not object.digest or not isinstance(object.digest, StringType):
            raise ObjectCubeException('Unable to update Object without a valid digest')

        sql = 'UPDATE OBJECTS ' \
              'SET NAME = %s, DIGEST = %s ' \
              'WHERE ID = %s ' \
              'RETURNING *'
        params = (object.name, object.digest, object.id)
        db_object = execute_sql_fetch_single(Object, sql, params)

        if db_object is None:
            raise ObjectCubeException('No Object found with id {}'.format(object.id))
        return db_object

    def delete(self, object):
        logger.debug('delete(): %s', repr(object))

        if object is None or not isinstance(object, Object):
            raise ObjectCubeException('Delete accepts only Object objects')
        if object.id is None or not isinstance(object.id, IntType):
            raise ObjectCubeException('Delete accepts only Object objects with valid ID')

        sql = 'DELETE ' \
              'FROM OBJECTS ' \
              'WHERE ID = %s ' \
              'RETURNING *'
        params = (object.id, )
        db_object = execute_sql_fetch_single(Object, sql, params)

        if db_object is None:
            raise ObjectCubeException('No Object found with id {}'.format(object.id))
        return None
