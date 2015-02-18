from psycopg2.extras import NamedTupleCursor

from objectcube.services.base import BaseTagService
from objectcube.contexts import Connection
from objectcube.vo import Tag
from objectcube.exceptions import (ObjectCubeDatabaseException,
                                   ObjectCubeException)


class TagServicePostgreSQL(BaseTagService):
    def get_by_value(self, value):
        return_list = []
        if not value:
            raise ObjectCubeException('Must give value')

        sql = "SELECT * FROM TAGS WHERE VALUE = '%s'" % value
        try:
            with Connection() as c:
                with c.cursor(cursor_factory=NamedTupleCursor) as cursor:
                    cursor.execute(sql)

                    for row in cursor.fetchall():
                        return_list.append(Tag(**row._asdict()))

            return return_list
        except Exception as e:
            raise ObjectCubeDatabaseException(e)

    def get_by_id(self, _id):
        if not _id or _id <= 0 or not isinstance(_id, int):
            raise ObjectCubeException('Id value must be a positive number')

        sql = "SELECT * FROM TAGS WHERE ID = {}".format(_id)

        try:
            with Connection() as c:
                with c.cursor(cursor_factory=NamedTupleCursor) as cursor:
                    cursor.execute(sql)
                    row = cursor.fetchone()
                    if row:
                        return Tag(**row._asdict())
        except Exception as e:
            raise ObjectCubeDatabaseException(e)

    def count(self):
        sql = """SELECT COUNT(ID) FROM TAGS"""
        try:
            with Connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql)
                    row = cursor.fetchone()
                    return int(row[0])
        except Exception as ex:
            raise ObjectCubeDatabaseException(ex)

    def get_tags(self, offset=0, limit=100):
        return_list = []

        sql = 'SELECT * FROM TAGS LIMIT %s OFFSET %s'
        try:
            with Connection() as c:
                with c.cursor(cursor_factory=NamedTupleCursor) as cursor:
                    cursor.execute(sql, (limit, offset))

                    for row in cursor.fetchall():
                        return_list.append(Tag(**row._asdict()))
        except Exception as ex:
            raise ObjectCubeDatabaseException(ex)

        return return_list

    def add_tag(self, tag):
        if tag.id:
            raise ObjectCubeException('Unable to to add tag that has id')

        sql = 'INSERT INTO TAGS(VALUE, DESCRIPTION, MUTABLE, TYPE, PLUGIN_ID) ' \
              'VALUES(%s, %s, %s, %s, %s) RETURNING ID'

        try:
            with Connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, (tag.value, tag.description,
                                         tag.mutable, tag.type, tag.plugin_id))
                    tag.id = cursor.fetchone()[0]
                    connection.commit()
        except Exception as ex:
            raise ObjectCubeDatabaseException(ex)
