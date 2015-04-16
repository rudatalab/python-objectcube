from psycopg2.extras import NamedTupleCursor

from utils import execute_sql_fetch_single, execute_sql_fetch_multiple
from objectcube.services.base import BaseTagService
from objectcube.vo import Concept, Plugin, Tag
from objectcube.exceptions import ObjectCubeException


class TagService(BaseTagService):

    def retrieve_by_value(self, value, offset=0, limit=100):
        if not value:
            raise ObjectCubeException('Must give value')

        sql = "SELECT * FROM TAGS WHERE VALUE = %s OFFSET %s LIMIT %s"
        params = (value, offset, limit)

        return execute_sql_fetch_multiple(Tag, sql, params)

    def retrieve_by_plugin(self, plugin, offset=0, limit=100):
        if not isinstance(plugin, Plugin) or not plugin.id:
            raise ObjectCubeException('Must give plugin with valid id')

        sql = "SELECT * FROM TAGS WHERE PLUGIN_ID = %s OFFSET %s LIMIT %s"
        params = (plugin.id, offset, limit)

        return execute_sql_fetch_multiple(Tag, sql, params)

    def retrieve_by_concept(self, concept, offset=0, limit=100):
        if not isinstance(concept, Concept) or not concept.id:
            raise ObjectCubeException('Must give concept with valid id')

        sql = "SELECT * FROM TAGS WHERE CONCEPT_ID = %s OFFSET %s LIMIT %s"
        params = (concept.id, offset, limit)

        return execute_sql_fetch_multiple(Tag, sql, params)

    def retrieve_by_id(self, _id):
        if not _id or _id <= 0 or not isinstance(_id, int):
            raise ObjectCubeException('Id value must be a positive number')

        sql = "SELECT * FROM TAGS WHERE ID = %s"
        params = (_id,)

        return execute_sql_fetch_single(Tag, sql, params)

    def count(self):
        sql = """SELECT COUNT(1) AS count FROM TAGS"""

        def extract_count(count):
            return count

        return execute_sql_fetch_single(extract_count, sql)

    def retrieve(self, offset=0, limit=100):
        return_list = []

        sql = 'SELECT * FROM TAGS LIMIT %s OFFSET %s'
        params = (limit, offset)

        return execute_sql_fetch_multiple(Tag, sql, params)

    def add(self, tag):
        if tag.id:
            raise ObjectCubeException('Unable to to add tag that has id')

        sql = 'INSERT INTO TAGS(VALUE, DESCRIPTION, MUTABLE, TYPE, ' \
              'CONCEPT_ID, PLUGIN_ID) VALUES(%s, %s, %s, %s, %s, %s) ' \
              'RETURNING *'
        params = (tag.value, tag.description,
                  tag.mutable, tag.type, tag.concept_id, tag.plugin_id)

        return execute_sql_fetch_single(Tag, sql, params)

    def update(self, tag):
        if not isinstance(tag, Tag) or not tag.id:
            raise ObjectCubeException('Must give tag with valid id')

        sql = 'UPDATE tags ' \
            'SET value       = %s ' \
            ',   description = %s ' \
            ',   mutable     = %s ' \
            ',   type        = %s ' \
            ',   concept_id  = %s ' \
            ',   plugin_id   = %s ' \
            'WHERE id = %s RETURNING *'
        params = (tag.value, tag.description, tag.mutable, tag.type,
                  tag.concept_id, tag.plugin_id, tag.id)

        return execute_sql_fetch_single(Tag, sql, params)

    def delete(self, tag):
        if not isinstance(tag, Tag) or not tag.id:
            raise ObjectCubeException('Must give tag with valid id')

        sql = 'DELETE FROM tags WHERE id = %s RETURNING *'
        params = (tag.id,)

        execute_sql_fetch_single(Tag, sql, params)

    def retrieve_or_create(self, tag):
        if not isinstance(tag, Tag) or tag.id:
            raise ObjectCubeException('Must give tag without valid id')

        sql = 'WITH p AS (' \
            ' SELECT %s::text as value ' \
            '      , %s::text as description ' \
            '      , %s::bool as mutable ' \
            '      , %s::int as type ' \
            '      , %s::int as concept_id ' \
            '      , %s::int as plugin_id ' \
            '), s AS (' \
            ' SELECT t.* FROM tags t, p' \
            ' WHERE (p.value is null or p.value = t.value) ' \
            '   AND (p.concept_id is null or p.concept_id = t.concept_id) ' \
            '   AND (p.plugin_id is null or p.plugin_id = t.plugin_id) ' \
            ' LIMIT 2' \
            '), i AS ( ' \
            ' INSERT INTO tags(VALUE, DESCRIPTION, MUTABLE, TYPE, ' \
            'CONCEPT_ID, PLUGIN_ID) (SELECT * from p' \
            '     WHERE NOT EXISTS (SELECT 1 FROM s)) ' \
            ' RETURNING *' \
            ') SELECT * FROM s UNION ALL SELECT * FROM i'
        params = (tag.value, tag.description,
                  tag.mutable, tag.type, tag.concept_id, tag.plugin_id)

        tags = execute_sql_fetch_multiple(Tag, sql, params)
        if len(tags) != 1:
            raise ObjectCubeException(
                "Ambiguous retrieve. Multiple candidates.")
        return tags[0]
