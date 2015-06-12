from psycopg2.extras import NamedTupleCursor

from utils import execute_sql_fetch_single, execute_sql_fetch_multiple
from objectcube.services.base import BaseTagService
from objectcube.vo import Concept, Plugin, Tag
from objectcube.exceptions import ObjectCubeException
from types import IntType, StringType, BooleanType

import logging
logger = logging.getLogger('postgreSQL: TagService')

class TagService(BaseTagService):

    def count(self):
        logger.debug('count()')
        sql = 'SELECT COUNT(1) AS count ' \
              'FROM TAGS'
        return execute_sql_fetch_single(lambda count: count, sql)

    def add(self, tag):
        logger.debug('add(): %s', repr(tag))

        # Need to give a tag, but it cannot have an ID
        if tag is None or not isinstance(tag, Tag):
            raise ObjectCubeException('Must give a valid tag')
        if not tag.id is None:
            raise ObjectCubeException('Unable to to add tag that has id')

        # NOT NULL attributes are VALUE and TYPE, need to check their existence and type
        if tag.value is None or not isinstance(tag.value, StringType):
            raise ObjectCubeException('Must give a valid tag value')
        if tag.type is None or not isinstance(tag.type, IntType):
            raise ObjectCubeException('Must give a valid tag type')

        # NULL attributes are DESCRIPTION, MUTABLE, CONCEPT_ID and PLUGIN_ID
        # These may be None, but if they are set then they must have the correct type
        #import pdb; pdb.set_trace()
        if not tag.description is None and not isinstance(tag.description, StringType):
            raise ObjectCubeException('If given, description must be a string')
        if not tag.mutable is None and not isinstance(tag.mutable, BooleanType):
            raise ObjectCubeException('If given, mutable must be valid')
        if not tag.concept_id is None and not isinstance(tag.concept_id, IntType):
            raise ObjectCubeException('If given, concept_id must be valid')
        if not tag.plugin_id is None and not isinstance(tag.plugin_id, IntType):
            raise ObjectCubeException('If given, plugin_id must be an integer')

        # Build the SQL expression, starting with NOT NULL attributes
        sql_attributes = 'VALUE, TYPE'
        sql_values = '%s, %s'
        params = (tag.value, tag.type)

        # Build the SQL expression, continuing with NULL attributes
        if not tag.description is None:
            sql_attributes += ', DESCRIPTION'
            sql_values += ',%s'
            params += (tag.description,)

        if not tag.mutable is None:
            sql_attributes += ', MUTABLE'
            sql_values += ',%s'
            params += (tag.mutable,)

        if not tag.concept_id is None:
            sql_attributes += ', CONCEPT_ID'
            sql_values += ',%s'
            params += (tag.concept_id,)

        if not tag.plugin_id is None:
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
        """
        retrieve_or_create() is intended for plugins.
        It must get a tag with (at least) value, type, concept_id and plugin_id.
        The id should not be given, but other attributes are optional.
        If a matching tag (based on the four mandatory attributes) is
        found in the database then that tag is returned.
        Otherwise, a new tag is created with the given values and returned.
        :param tag: Tag
        :return: Tag
        """
        logger.debug('retrieve_or_create(): %s', repr(tag))

        # Need to give a tag, but cannot have ID
        if tag is None or not isinstance(tag, Tag):
            raise ObjectCubeException('Must give a valid tag')
        if not tag.id is None:
            raise ObjectCubeException('Unable to to add tag that has id')

        # REQUIRED attributes are VALUE, TYPE, CONCEPT_ID, PLUGIN_ID
        # We need to check their existence and type
        if tag.value is None or not isinstance(tag.value, StringType):
            raise ObjectCubeException('Must give a valid tag value')
        if tag.type is None or not isinstance(tag.type, IntType):
            raise ObjectCubeException('Must give a valid tag type')
        if tag.concept_id is None or not isinstance(tag.concept_id, IntType):
            raise ObjectCubeException('Must give a valid concept_id')
        if tag.plugin_id is None or not isinstance(tag.plugin_id, IntType):
            raise ObjectCubeException('Must give a valid plugin_id')

        # OPTIONAL attributes are DESCRIPTION and MUTABLE
        # These may be None, but if they are set then they must have the correct type
        if not tag.description is None and not isinstance(tag.description, StringType):
            raise ObjectCubeException('If given, description must be a string')
        if not tag.mutable is None and not isinstance(tag.mutable, BooleanType):
            raise ObjectCubeException('If given, mutable must be valid')

        # Try to retrieve the single tag from the database
        sql = 'SELECT * ' \
              'FROM TAGS ' \
              'WHERE VALUE = %s ' \
              '  AND TYPE = %s ' \
              '  AND CONCEPT_ID = %s ' \
              '  AND PLUGIN_ID = %s ' \
              'OFFSET %s LIMIT %s'
        params = (tag.value, tag.type, tag.concept_id, tag.plugin_id, 0, 2)
        tags = execute_sql_fetch_multiple(Tag, sql, params)

        # Check for duplicates, this should not happen
        if len(tags) > 1:
            raise ObjectCubeException('Cannot have duplicate tags from plugins')

        # If the single tag exists, return it
        if len(tags) == 1:
            return tags[0]

        # Tag does not exist; create it
        # Should be safe to use add() as all parameters have been checked
        # Can still give errors on foreign keys, but that is normal
        return self.add(tag)

    def update(self, tag):
        """
        update() must get a tag with valid id.
        It updates the value and description columns, if they are set,
        and concept_id if it is set and if plugin_id is not given in the database.
        Other columns cannot be changed and are therefore ignored.
        Three situations raise an exception: The id is invalid; mutable is True; and
        a modification of concept_id is attempted for a plugin-generated tag.
        :param tag: Tag
        :return: Tag
        """
        logger.debug('update(): %s', repr(tag))

        # Need to give a tag, must have ID
        if tag is None or not isinstance(tag, Tag):
            raise ObjectCubeException('Must give a valid tag')
        if tag.id is None or not isinstance(tag.id, IntType):
            raise ObjectCubeException('Must give tag with valid id')

        # OPTIONAL attributes are all others
        # These may be None, but if they are set then they must have the correct type
        if not tag.value is None and not isinstance(tag.value, StringType):
            raise ObjectCubeException('If given, value must be a string')
        if not tag.description is None and not isinstance(tag.description, StringType):
            raise ObjectCubeException('If given, description must be a string')
        if not tag.type is None and not isinstance(tag.type, IntType):
            raise ObjectCubeException('If given, type must be an integer')
        if not tag.mutable is None and not isinstance(tag.mutable, BooleanType):
            raise ObjectCubeException('If given, mutable must be boolean')
        if not tag.concept_id is None and not isinstance(tag.concept_id, IntType):
            raise ObjectCubeException('If given, concept_id must be an integer')
        if not tag.plugin_id is None and not isinstance(tag.plugin_id, IntType):
            raise ObjectCubeException('If given, plugin_id must be an integer')

        # Get the old tag to verify that it exists, and run some more checks
        old_tag = self.retrieve_by_id(tag.id)
        if old_tag is None:
            raise ObjectCubeException('Updating a non-existing tag')
        if not old_tag.mutable is None and not old_tag.mutable:
            raise ObjectCubeException('Cannot change a non-mutable concept')
        if not old_tag.plugin_id is None and tag.concept_id <> old_tag.concept_id:
            raise ObjectCubeException('Cannot change concept on a plugin-generated tag')

        # Build the SQL expression for the given attributes
        params = tuple()
        attributes = []
        if not tag.value is None:
            attributes.append('VALUE = %s')
            params += (tag.value, )
        if not tag.description is None:
            attributes.append('DESCRIPTION = %s')
            params += (tag.description, )
        if not tag.concept_id is None:
            attributes.append('CONCEPT_ID = %s')
            params += (tag.concept_id, )

        sql_attributes = ', '
        params += (tag.id, )

        sql = 'UPDATE TAGS SET ' + \
              sql_attributes.join(attributes) + \
              ' WHERE ID = %s RETURNING *'
        return execute_sql_fetch_single(Tag, sql, params)

    def retrieve(self, offset=0, limit=10):
        logger.debug('retrieve()')
        sql = 'SELECT * ' \
              'FROM TAGS ' \
              'LIMIT %s OFFSET %s'
        params = (limit, offset)
        return execute_sql_fetch_multiple(Tag, sql, params)

    def retrieve_by_value(self, value, offset=0, limit=10):
        logger.debug('retrieve_by_value(): %s', repr(value))

        if value is None or not isinstance(value, StringType):
            raise ObjectCubeException('Must give string value')

        sql = 'SELECT * ' \
              'FROM TAGS ' \
              'WHERE VALUE = %s ' \
              'OFFSET %s LIMIT %s'
        params = (value, offset, limit)
        return execute_sql_fetch_multiple(Tag, sql, params)

    def retrieve_by_plugin(self, plugin, offset=0, limit=10):
        logger.debug('retrieve_by_plugin(): %s', repr(plugin))

        if plugin is None or not isinstance(plugin, Plugin) \
                or plugin.id is None or not isinstance(plugin.id, IntType):
            raise ObjectCubeException('Must give plugin with valid id')

        sql = 'SELECT * ' \
              'FROM TAGS ' \
              'WHERE PLUGIN_ID = %s ' \
              'OFFSET %s LIMIT %s'
        params = (plugin.id, offset, limit)
        return execute_sql_fetch_multiple(Tag, sql, params)

    def retrieve_by_concept(self, concept, offset=0, limit=10):
        logger.debug('retrieve_by_concept(): %s', repr(concept))

        if concept is None or not isinstance(concept, Concept) \
                or concept.id is None or not isinstance(concept.id, IntType):
            raise ObjectCubeException('Must give concept with valid id')

        sql = 'SELECT * ' \
              'FROM TAGS ' \
              'WHERE CONCEPT_ID = %s ' \
              'OFFSET %s LIMIT %s'
        params = (concept.id, offset, limit)
        return execute_sql_fetch_multiple(Tag, sql, params)

    def retrieve_by_id(self, id):
        logger.debug('retrieve_by_id(): %s', repr(id))

        if id is None or not isinstance(id, IntType):
            raise ObjectCubeException('Id value must be number')

        sql = 'SELECT * ' \
              'FROM TAGS ' \
              'WHERE ID = %s'
        params = (id,)
        return execute_sql_fetch_single(Tag, sql, params)

    def delete(self, tag):
        logger.debug('delete(): %s', repr(tag))

        if tag is None or not isinstance(tag, Tag) \
                or tag.id is None or not isinstance(tag.id, IntType) :
            raise ObjectCubeException('Must give tag with valid id')

        sql = 'DELETE ' \
              'FROM tags ' \
              'WHERE id = %s ' \
              'RETURNING *'
        params = (tag.id,)
        execute_sql_fetch_single(Tag, sql, params)
        return None
