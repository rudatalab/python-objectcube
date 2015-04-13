from psycopg2.extras import NamedTupleCursor

from utils import execute_single_sql, retrieve_multiple_tags
from objectcube.services.base import BaseTagService
from objectcube.contexts import Connection
from objectcube.vo import Tag
from objectcube.exceptions import (ObjectCubeDatabaseException,
                                   ObjectCubeException)


class TagService(BaseTagService):
    def retrieve_by_value(self, value, offset=0, limit=100):
        if not value:
            raise ObjectCubeException('Must give value')

        sql = "SELECT * FROM TAGS WHERE VALUE = %s OFFSET %s LIMIT %s"
        params = (value, offset, limit)

        return retrieve_multiple_tags(Tag, sql, params)

    def retrieve_by_plugin(self, plugin, offset=0, limit=100):
        if not plugin:
            raise ObjectCubeException('Must give plugin')

        sql = "SELECT * FROM TAGS WHERE PLUGIN_ID = %s OFFSET %s LIMIT %s"
        params = (plugin, offset, limit)

        return retrieve_multiple_tags(Tag, sql, params)

    def retrieve_by_concept(self, concept, offset=0, limit=100):
        if not concept:
            raise ObjectCubeException('Must give concept')

        sql = "SELECT * FROM TAGS WHERE CONCEPT = %s OFFSET %s LIMIT %s"
        params = (concept, offset, limit)

        return retrieve_multiple_tags(Tag, sql, params)

    def retrieve_by_id(self, _id):
        if not _id or _id <= 0 or not isinstance(_id, int):
            raise ObjectCubeException('Id value must be a positive number')

        sql = "SELECT * FROM TAGS WHERE ID = %s"

        try:
            with Connection() as c:
                with c.cursor(cursor_factory=NamedTupleCursor) as cursor:
                    cursor.execute(sql, (_id,))
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

    def retrieve(self, offset=0, limit=100):
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

    def add(self, tag):
        if tag.id:
            raise ObjectCubeException('Unable to to add tag that has id')

        sql = 'INSERT INTO TAGS(VALUE, DESCRIPTION, MUTABLE, TYPE, ' \
              'PLUGIN_ID) VALUES(%s, %s, %s, %s, %s) RETURNING *'
        params = (tag.value, tag.description,
                  tag.mutable, tag.type, tag.plugin_id)

        return execute_single_sql(Tag, sql, params)

    def update(self, tag):
        if not isinstance(tag, Tag) or not tag.id:
            raise ObjectCubeException('Must give tag with valid id')

        sql = 'UPDATE tags ' \
            'SET value       = %s ' \
            ',   description = %s ' \
            ',   mutable     = %s ' \
            ',   type        = %s ' \
            ',   plugin_id   = %s ' \
            'WHERE id = %s RETURNING *'
        params = (tag.value, tag.description,
                  tag.mutable, tag.type, tag.plugin_id, tag.id)

        return execute_single_sql(Tag, sql, params)

    def delete(self, tag):
        if not isinstance(tag, Tag) or not tag.id:
            raise ObjectCubeException('Must give tag with valid id')

        sql = 'DELETE FROM tags WHERE id = %s RETURNING *'
        params = (tag.id,)

        execute_single_sql(Tag, sql, params)

    def retrieve_or_create(self, tag):
        if not isinstance(tag, Tag) or tag.id:
            raise ObjectCubeException('Must give tag without valid id')

        sql = 'WITH p AS (' \
            ' SELECT %s::text as value ' \
            '      , %s::text as description ' \
            '      , %s::bool as mutable ' \
            '      , %s::int as type ' \
            '      , %s::int as plugin_id ' \
            '), s AS (' \
            ' SELECT t.* FROM tags t, p' \
            ' WHERE (p.value is null or p.value = t.value) ' \
            '   AND (p.plugin_id is null or p.plugin_id = t.plugin_id) ' \
            ' LIMIT 2' \
            '), i AS ( ' \
            ' INSERT INTO tags(VALUE, DESCRIPTION, MUTABLE, TYPE, ' \
            'PLUGIN_ID) (SELECT * from p' \
            '     WHERE NOT EXISTS (SELECT 1 FROM s)) ' \
            ' RETURNING *' \
            ') SELECT * FROM s UNION ALL SELECT * FROM i'
        params = (tag.value, tag.description,
                  tag.mutable, tag.type, tag.plugin_id)

        try:
            with Connection() as c:
                with c.cursor(cursor_factory=NamedTupleCursor) as cursor:
                    cursor.execute(sql, params)
                    rows = cursor.fetchall()
                    if len(rows) > 1:
                        raise ObjectCubeException(
                            "Ambiguous retrieve. Multiple candidates.")
                    c.commit()
                    return Tag(**rows[0]._asdict())
        except ObjectCubeException:
            raise
        except Exception as ex:
            raise ObjectCubeDatabaseException(ex)
