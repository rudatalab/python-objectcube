import itertools

from psycopg2.extras import NamedTupleCursor

from objectcube.services.base import BaseObjectService
from objectcube.contexts import Connection
from objectcube.exceptions import (ObjectCubeDatabaseException,
                                   ObjectCubeException)
from objectcube.utils import md5_from_stream
from objectcube.vo import Object, Tag


class ObjectService(BaseObjectService):
    def count(self):
        sql = """SELECT COUNT(ID) FROM OBJECTS"""
        try:
            with Connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql)
                    row = cursor.fetchone()
                    return int(row[0])
        except Exception as ex:
            raise ObjectCubeDatabaseException(ex)

    def add_tags_to_objects(self, objects, tags):
        """
        Add tags to objects. All tags in the tags parameter
        will be applied to all objects in the objects parameter.
        """
        bulk_size = 10

        if not objects or not tags:
            raise ObjectCubeException('Invalid arguments')

        if not isinstance(objects, list):
            objects = [objects]

        if not isinstance(tags, list):
            tags = [tags]

        if isinstance(objects[0], Object):
            objects = [x.id for x in objects]

        if isinstance(tags[0], Tag):
            tags = [x.id for x in tags]

        insert_values = itertools.product(objects, tags)

        sql = "INSERT INTO OBJECT_TAG(OBJECT_ID, TAG_ID) VALUES(%s, %s)"
        try:
            with Connection() as connection:
                cursor = connection.cursor()
                bulk_values = []

                for v in insert_values:
                    bulk_values.append((v[0], v[1]))
                    if len(bulk_values) > bulk_size:
                        cursor.executemany(sql, tuple(bulk_values))
                        bulk_values = []

                if len(bulk_values) != 0:
                    cursor.executemany(sql, tuple(bulk_values))

        except Exception as ex:
            raise ObjectCubeDatabaseException(ex)

    def get_objects_by_tags(self, tags):
        """
        Fetch objects that have been applied with tags in tags
        """
        if isinstance(tags, Tag):
            tags = [tags]

        return_list = []
        if not tags:
            raise ObjectCubeException('Tags parameter must be set')

        if isinstance(tags[0], Tag):
            tags = [tag.id for tag in tags]

        # remove duplicates in the tags array
        tags = set(tags)

        # TODO (hlysig) we are looping way to often over this collection!
        ids = ','.join([str(x) for x in tags])
        sql = 'select o.id, o.name, o.digest from objects o join object_tag' \
              ' t on t.object_id = o.id where t.tag_id in ({})'.format(ids)

        try:
            with Connection() as c:
                with c.cursor(cursor_factory=NamedTupleCursor) as cursor:
                    cursor.execute(sql)
                    for row in cursor.fetchall():
                        return_list.append(Object(**row._asdict()))
            return return_list
        except Exception as e:
            raise ObjectCubeDatabaseException(e)

    def add(self, stream, name):
        if not name:
            raise ObjectCubeException('Name is required')

        if not stream:
            raise ObjectCubeException('Stream is broken')

        file_digest = md5_from_stream(stream)
        sql = 'INSERT INTO OBJECTS(NAME, DIGEST) values (%s, %s) RETURNING ID'

        try:
            with Connection() as connection:
                cursor = connection.cursor()
                cursor.execute(sql, (name, file_digest))
                row = cursor.fetchone()
                return Object(**{
                    'id': row[0],
                    'name': name,
                    'digest': file_digest
                })

        except Exception as ex:
            raise ObjectCubeDatabaseException(ex)

    def get_by_id(self, _id):
        sql = "SELECT ID, NAME, DIGEST FROM OBJECTS WHERE ID=%s"
        try:
            with Connection() as c:
                with c.cursor(cursor_factory=NamedTupleCursor) as cursor:
                    cursor.execute(sql, (_id,))
                    row = cursor.fetchone()
                    return Object(**row._asdict())

        except Exception as e:
            raise ObjectCubeDatabaseException(e)

    def get_objects(self, offset=0, limit=10):
        return_list = []

        sql = 'SELECT ID, NAME, DIGEST FROM OBJECTS LIMIT %s OFFSET %s'
        try:
            with Connection() as c:
                with c.cursor(cursor_factory=NamedTupleCursor) as cursor:
                    cursor.execute(sql, (limit, offset))

                    for row in cursor.fetchall():
                        return_list.append(Object(**row._asdict()))
        except Exception as ex:
            raise ObjectCubeDatabaseException(ex)

        return return_list
