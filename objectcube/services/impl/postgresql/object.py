from utils import execute_sql_fetch_single, execute_sql_fetch_multiple
from objectcube.services.base import BaseObjectService
from objectcube.exceptions import ObjectCubeException
from objectcube.data_objects import Object, Tag
from types import LongType, UnicodeType
from logging import getLogger


class ObjectService(BaseObjectService):
    def __init__(self):
        super(ObjectService, self).__init__()
        self.logger = getLogger('postgreSQL: ObjectService')

    def count(self):
        self.logger.debug('count()')
        sql = 'SELECT COUNT(1) AS count ' \
              'FROM OBJECTS'
        return execute_sql_fetch_single(lambda count: count, sql)

    def add(self, object_):
        self.logger.debug('add(): %s', repr(object_))

        if not isinstance(object_, Object):
            raise ObjectCubeException('Function requires valid Object')
        if object_.id is not None:
            raise ObjectCubeException('Function must not get id')

        sql = 'INSERT ' \
              'INTO OBJECTS (NAME, DIGEST) ' \
              'VALUES (%s, %s) ' \
              'RETURNING *'
        params = (object_.name, object_.digest)
        return execute_sql_fetch_single(Object, sql, params)

    def update(self, object_):
        self.logger.debug('update(): %s', repr(object_))

        if not isinstance(object_, Object):
            raise ObjectCubeException('Function requires valid Object')
        if not object_.id:
            raise ObjectCubeException('Function requires valid id')

        sql = 'UPDATE OBJECTS ' \
              'SET NAME = %s, DIGEST = %s ' \
              'WHERE ID = %s ' \
              'RETURNING *'
        params = (object_.name, object_.digest, object_.id)
        db_object = execute_sql_fetch_single(Object, sql, params)

        if not db_object:
            raise ObjectCubeException('No Object found to update')
        return db_object

    def delete(self, object_):
        self.logger.debug('delete(): %s', repr(object_))

        if not isinstance(object_, Object):
            raise ObjectCubeException('Function requires valid Object')
        if not object_.id:
            raise ObjectCubeException('Function requires valid id')

        sql = 'DELETE ' \
              'FROM OBJECTS ' \
              'WHERE ID = %s ' \
              'RETURNING *'
        params = (object_.id, )
        db_object = execute_sql_fetch_single(Object, sql, params)

        if not db_object:
            raise ObjectCubeException('No Object found to delete')
        return None

    def delete_by_id(self, id_):
        self.logger.debug('delete_by_id(): %s', repr(id_))

        if not isinstance(id_, LongType):
            raise ObjectCubeException('Function requires valid id')

        sql = 'DELETE ' \
              'FROM OBJECTS ' \
              'WHERE ID = %s ' \
              'RETURNING *'
        params = (id_, )
        db_object = execute_sql_fetch_single(Object, sql, params)

        if not db_object:
            raise ObjectCubeException('No Object found to delete')
        return None

    def retrieve_by_id(self, id_):
        self.logger.debug('retrieve_by_id(): %s', repr(id_))

        if not isinstance(id_, LongType):
            raise ObjectCubeException('Function requires valid id')

        sql = 'SELECT * ' \
              'FROM OBJECTS ' \
              'WHERE ID = %s'
        params = (id_,)
        return execute_sql_fetch_single(Object, sql, params)

    def retrieve(self, offset=0L, limit=10L):
        self.logger.debug('retrieve(): %s / %s', repr(offset), repr(limit))

        if not isinstance(offset, LongType):
            raise ObjectCubeException('Function requires valid offset')
        if not isinstance(limit, LongType):
            raise ObjectCubeException('Function requires valid limit')

        sql = 'SELECT ID, NAME, DIGEST ' \
              'FROM OBJECTS ' \
              'OFFSET %s LIMIT %s'
        params = (offset, limit)
        return execute_sql_fetch_multiple(Object, sql, params)

    def retrieve_by_regex(self, name, offset=0L, limit=10L):
        self.logger.debug('retrieve_by_regex(): %s / %s / %s',
                          repr(name), repr(offset), repr(limit))

        if not isinstance(name, UnicodeType):
            raise ObjectCubeException('Function requires valid name regex')

        if not isinstance(offset, LongType):
            raise ObjectCubeException('Function requires valid offset')
        if not isinstance(limit, LongType):
            raise ObjectCubeException('Function requires valid limit')

        sql = 'SELECT ID, NAME, DIGEST ' \
              'FROM OBJECTS ' \
              'WHERE NAME ~ %s ' \
              'OFFSET %s LIMIT %s'
        params = (name, offset, limit)
        return execute_sql_fetch_multiple(Object, sql, params)

    def retrieve_by_tag(self, tag, offset=0L, limit=10L):
        self.logger.debug('retrieve_by_tag(): %s / %s / %s',
                          repr(tag), repr(offset), repr(limit))

        if not isinstance(tag, Tag):
            raise ObjectCubeException('Function requires valid Tag')
        if not tag.id:
            raise ObjectCubeException('Function requires valid Tag id')

        if not isinstance(offset, LongType):
            raise ObjectCubeException('Function requires valid offset')
        if not isinstance(limit, LongType):
            raise ObjectCubeException('Function requires valid limit')

        sql = 'SELECT O.ID, O.NAME, O.DIGEST ' \
              'FROM OBJECTS O JOIN TAGGINGS T ON O.ID = T.OBJECT_ID ' \
              'WHERE T.TAG_ID = %s ' \
              'OFFSET %s LIMIT %s'
        params = (tag.id, offset, limit)
        return execute_sql_fetch_multiple(Object, sql, params)
