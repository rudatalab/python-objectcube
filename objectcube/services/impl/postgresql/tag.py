from utils import execute_sql_fetch_single, execute_sql_fetch_multiple
from objectcube.services.base import BaseTagService
from objectcube.data_objects import Concept, Plugin, Tag
from objectcube.exceptions import ObjectCubeException
from types import LongType, UnicodeType, NoneType
from logging import getLogger


class TagService(BaseTagService):
    def __init__(self):
        super(TagService, self).__init__()
        self.logger = getLogger('postgreSQL: TagService')

    def count(self):
        self.logger.debug('count()')
        sql = 'SELECT COUNT(1) AS count ' \
              'FROM TAGS'
        return execute_sql_fetch_single(lambda count: count, sql)

    def add(self, tag):
        self.logger.debug('add(): %s', repr(tag))

        # Need to give a tag, but it cannot have an ID
        if not isinstance(tag, Tag):
            raise ObjectCubeException('Function requires valid Tag')
        if tag.id is not None:
            raise ObjectCubeException('Function must not get Tag id')

        # Build the SQL expression, starting with required attributes
        sql_attributes = 'VALUE, DESCRIPTION, TYPE, MUTABLE'
        sql_values = '%s, %s, %s, %s'
        params = (tag.value, tag.description, tag.type, tag.mutable)

        # Build the SQL expression, continuing with optional attributes
        if tag.concept_id is not None:
            sql_attributes += ', CONCEPT_ID'
            sql_values += ',%s'
            params += (tag.concept_id,)
        if tag.plugin_id is not None:
            sql_attributes += ', PLUGIN_ID'
            sql_values += ',%s'
            params += (tag.plugin_id,)

        sql = 'INSERT INTO TAGS (' + \
              sql_attributes + \
              ') VALUES (' \
              + sql_values + \
              ') RETURNING *'
        return execute_sql_fetch_single(Tag, sql, params)

    def retrieve_or_create(self, tag):
        self.logger.debug('retrieve_or_create(): %s', repr(tag))

        # Need to give a tag, but cannot have ID
        if not isinstance(tag, Tag):
            raise ObjectCubeException('Function requires valid Tag')
        if tag.id is not None:
            raise ObjectCubeException('Function must not get Tag id')

        # For the retrieval part, the following are REQUIRED attributes:
        # VALUE (always set), TYPE (always set), CONCEPT_ID, PLUGIN_ID
        # We need to check their existence but the type will be correct
        if not tag.concept_id:
            raise ObjectCubeException('Function requires valid concept_id')
        if not tag.plugin_id:
            raise ObjectCubeException('Function requires valid plugin_id')

        # Try to retrieve the single tag from the database
        sql = 'SELECT * ' \
              'FROM TAGS ' \
              'WHERE VALUE = %s ' \
              '  AND TYPE = %s ' \
              '  AND CONCEPT_ID = %s ' \
              '  AND PLUGIN_ID = %s ' \
              'OFFSET %s LIMIT %s'
        params = (tag.value, tag.type, tag.concept_id, tag.plugin_id, 0L, 2L)
        tags = execute_sql_fetch_multiple(Tag, sql, params)

        # Check for duplicates, this should not happen
        if len(tags) > 1:
            raise ObjectCubeException('Panic: No plugin duplicates allowed')

        # If the single tag exists, return it
        if len(tags) == 1:
            return tags[0]

        # Tag does not exist; create it
        # Should be safe to use add() as all parameters have been checked
        # Can still give errors on foreign keys, but that is normal
        return self.add(tag)

    def update(self, tag):
        self.logger.debug('update(): %s', repr(tag))

        # Need to give a tag, must have ID
        if not isinstance(tag, Tag):
            raise ObjectCubeException('Function requires valid Tag')
        if not tag.id:
            raise ObjectCubeException('Function requires valid Tag id')

        # Get the old tag to verify that it exists,
        # and then run some business logic checks
        old = self.retrieve_by_id(tag.id)
        if not old:
            raise ObjectCubeException('No Tag found to update')
        if not old.mutable:
            raise ObjectCubeException('Cannot change a non-mutable concept')
        if tag.plugin_id != old.plugin_id:
            raise ObjectCubeException('Cannot change generating plugin ')
        if old.plugin_id and tag.concept_id != old.concept_id:
            raise ObjectCubeException('Cannot change plugin-generated concept')

        # Build the SQL expression for the attributes that may be changed
        params = tuple()
        attributes = []

        if tag.value != old.value:
            attributes.append('VALUE = %s')
            params += (tag.value, )

        if tag.description != old.description:
            attributes.append('DESCRIPTION = %s')
            params += (tag.description, )

        if tag.concept_id != old.concept_id:
            attributes.append('CONCEPT_ID = %s')
            params += (tag.concept_id, )

        if tag.type != old.type:
            attributes.append('TYPE = %s')
            params += (tag.type, )

        sql_attributes = ', '
        params += (tag.id, )

        sql = 'UPDATE TAGS SET ' + \
              sql_attributes.join(attributes) + \
              ' WHERE ID = %s RETURNING *'
        return execute_sql_fetch_single(Tag, sql, params)

    def delete_by_id(self, id_):
        self.logger.debug('delete(): %s', repr(id_))

        if not isinstance(id_, LongType):
            raise ObjectCubeException('Function requires valid id')

        sql = 'DELETE ' \
              'FROM tags ' \
              'WHERE id = %s ' \
              'RETURNING *'
        params = (id_,)
        db_tag = execute_sql_fetch_single(Tag, sql, params)

        if not db_tag:
            raise ObjectCubeException('No Tag found to delete')
        return None

    def delete(self, tag):
        self.logger.debug('delete(): %s', repr(tag))

        if not isinstance(tag, Tag):
            raise ObjectCubeException('Function requires valid Tag')
        if not tag.id:
            raise ObjectCubeException('Function requires valid Tag id')

        sql = 'DELETE ' \
              'FROM tags ' \
              'WHERE id = %s ' \
              'RETURNING *'
        params = (tag.id,)
        db_tag = execute_sql_fetch_single(Tag, sql, params)

        if not db_tag:
            raise ObjectCubeException('No Tag found to delete')
        return None

    def retrieve_by_id(self, id_):
        self.logger.debug('retrieve_by_id(): %s', repr(id_))

        if not isinstance(id_, LongType):
            raise ObjectCubeException('Function requires valid Tag id')

        sql = 'SELECT * ' \
              'FROM TAGS ' \
              'WHERE ID = %s'
        params = (id_,)
        return execute_sql_fetch_single(Tag, sql, params)

    def retrieve(self, offset=0L, limit=10L):
        self.logger.debug('retrieve()')

        if not isinstance(offset, LongType):
            raise ObjectCubeException('Function requires valid offset')
        if not isinstance(limit, LongType):
            raise ObjectCubeException('Function requires valid limit')

        sql = 'SELECT * ' \
              'FROM TAGS ' \
              'LIMIT %s OFFSET %s'
        params = (limit, offset)
        return execute_sql_fetch_multiple(Tag, sql, params)

    def retrieve_by_value(self, value, offset=0L, limit=10L):
        self.logger.debug('retrieve_by_value(): %s', repr(value))

        if not isinstance(value, UnicodeType):
            raise ObjectCubeException('Function requires valid value')
        if not isinstance(offset, LongType):
            raise ObjectCubeException('Function requires valid offset')
        if not isinstance(limit, LongType):
            raise ObjectCubeException('Function requires valid limit')

        sql = 'SELECT * ' \
              'FROM TAGS ' \
              'WHERE VALUE = %s ' \
              'OFFSET %s LIMIT %s'
        params = (value, offset, limit)
        return execute_sql_fetch_multiple(Tag, sql, params)

    def retrieve_by_regex(self, value=None, description=None,
                          offset=0L, limit=10L):
        self.logger.debug('retrieve_or_create(): %s / %s / %s / %s',
                          repr(value), repr(description),
                          repr(offset), repr(limit))

        if not isinstance(value, (UnicodeType, NoneType)):
            raise ObjectCubeException('Function requires valid name regex')
        if not isinstance(description, (UnicodeType, NoneType)):
            raise ObjectCubeException('Function requires valid desc regex')
        if not value and not description:
            raise ObjectCubeException('Function requires one valid regex')

        if not isinstance(offset, LongType):
            raise ObjectCubeException('Function requires valid offset')
        if not isinstance(limit, LongType):
            raise ObjectCubeException('Function requires valid limit')

        if value and description:
            sql = 'SELECT * ' \
                  'FROM TAGS ' \
                  'WHERE VALUE ~ %s ' \
                  '  AND DESCRIPTION ~ %s' \
                  'OFFSET %s LIMIT %s'
            params = (value, description, offset, limit)
        elif value:
            sql = 'SELECT * ' \
                  'FROM TAGS ' \
                  'WHERE VALUE ~ %s ' \
                  'OFFSET %s LIMIT %s'
            params = (value, offset, limit)
        else:
            sql = 'SELECT * ' \
                  'FROM TAGS ' \
                  'WHERE DESCRIPTION ~ %s ' \
                  'OFFSET %s LIMIT %s'
            params = (description, offset, limit)
        return execute_sql_fetch_multiple(Tag, sql, params)

    def retrieve_by_plugin_id(self, plugin_id, offset=0L, limit=10L):
        self.logger.debug('retrieve_by_plugin_id(): %s', repr(plugin_id))

        if not isinstance(plugin_id, LongType):
            raise ObjectCubeException('Function requires valid Plugin id')

        if not isinstance(offset, LongType):
            raise ObjectCubeException('Function requires valid offset')
        if not isinstance(limit, LongType):
            raise ObjectCubeException('Function requires valid limit')

        sql = 'SELECT * ' \
              'FROM TAGS ' \
              'WHERE PLUGIN_ID = %s ' \
              'OFFSET %s LIMIT %s'
        params = (plugin_id, offset, limit)
        return execute_sql_fetch_multiple(Tag, sql, params)

    def retrieve_by_concept_id(self, concept_id, offset=0L, limit=10L):
        self.logger.debug('retrieve_by_concept_id(): %s', repr(concept_id))

        if not isinstance(concept_id, LongType):
            raise ObjectCubeException('Function requires valid Concept id')

        if not isinstance(offset, LongType):
            raise ObjectCubeException('Function requires valid offset')
        if not isinstance(limit, LongType):
            raise ObjectCubeException('Function requires valid limit')

        sql = 'SELECT * ' \
              'FROM TAGS ' \
              'WHERE CONCEPT_ID = %s ' \
              'OFFSET %s LIMIT %s'
        params = (concept_id, offset, limit)
        return execute_sql_fetch_multiple(Tag, sql, params)
