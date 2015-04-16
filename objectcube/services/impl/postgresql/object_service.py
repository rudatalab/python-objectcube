
import logging
from utils import execute_sql_fetch_single, execute_sql_fetch_multiple

from objectcube.services.base import BaseObjectService
from objectcube.exceptions import ObjectCubeException
from objectcube.vo import Object, Tag

logger = logging.getLogger('postgreSQL: ObjectService')


class ObjectService(BaseObjectService):
    def __init__(self):
        super(ObjectService, self).__init__()

    def count(self):
        sql = """SELECT COUNT(1) AS count FROM OBJECTS"""

        def extract_count(count):
            return count

        return execute_sql_fetch_single(extract_count, sql)

    def add(self, _object):
        if not isinstance(_object, Object) or not _object.name or \
                not _object.digest or _object.id:
            raise ObjectCubeException(
                'Must give object with valid name, digest and without id')

        sql = 'INSERT INTO OBJECTS(NAME, DIGEST) values (%s, %s) RETURNING *'
        params = (_object.name, _object.digest)

        return execute_sql_fetch_single(Object, sql, params)

    def retrieve_by_id(self, _id):
        sql = "SELECT * FROM OBJECTS WHERE ID=%s"
        params = (_id,)

        return execute_sql_fetch_single(Object, sql, params)

    def retrieve(self, offset=0, limit=10):
        return_list = []

        sql = 'SELECT ID, NAME, DIGEST FROM OBJECTS OFFSET %s LIMIT %s'
        params = (offset, limit)

        return execute_sql_fetch_multiple(Object, sql, params)

    def retrieve_by_tag(self, tag, offset=0, limit=10):
        if not isinstance(tag, Tag) or not tag.id:
            raise ObjectCubeException('Must give tag with valid id')

        sql = 'SELECT o.* FROM objects o WHERE EXISTS ' \
              '(SELECT 1 FROM tags t JOIN object_tag ot on '\
              't.id = ot.tag_id WHERE ot.object_id = o.id AND t.id = %s) ' \
              'OFFSET %s LIMIT %s'
        params = (tag.id, offset, limit)

        return execute_sql_fetch_multiple(Object, sql, params)

    def update(self, _object):
        logger.debug('Calling update')

        if not isinstance(_object, Object):
            message = 'Parameter must be of type {}'.format(Object.__name__)
            logger.error(message)
            raise ObjectCubeException(message)

        if not _object.id:
            message = 'Must give object with valid id'
            logger.error(message)
            raise ObjectCubeException(message)

        if not self.retrieve_by_id(_object.id):
            raise ObjectCubeException(
                'No object found with id {}'.format(_object.id))

        sql = 'UPDATE OBJECTS SET NAME=%s RETURNING *'
        params = (_object.name,)

        return execute_sql_fetch_single(Object, sql, params)

    def delete(self, _object):
        if not isinstance(_object, Object) or not _object.id:
            raise ObjectCubeException('Must give object with valid id')

        sql = 'DELETE FROM OBJECTS WHERE ID=%s RETURNING *'
        params = (_object.id, )

        return bool(execute_sql_fetch_single(Object, sql, params))
