from objectcube.vo import Concept
from objectcube.exceptions import ObjectCubeException
from objectcube.services.base import BaseConceptService
from types import LongType, UnicodeType
from utils import execute_sql_fetch_single, execute_sql_fetch_multiple

import logging
logger = logging.getLogger('PostgreSQL:ConceptService')

class ConceptService(BaseConceptService):
    def count(self):
        logger.debug('count()')
        sql = 'SELECT COUNT(1) AS count ' \
              'FROM CONCEPTS'
        return execute_sql_fetch_single(lambda count: count, sql)

    def add(self, concept):
        logger.debug('add(): %s', repr(concept))

        if concept is None or not isinstance(concept, Concept):
            raise ObjectCubeException('Function requires valid concept')
        if concept.title is None or not isinstance(concept.title, UnicodeType):
            raise ObjectCubeException('Function requires valid title')
        if concept.description is None or not isinstance(concept.description, UnicodeType):
            raise ObjectCubeException('Function requires valid description')
        if concept.id is not None:
            raise ObjectCubeException('Function must not get ID')

        sql = 'INSERT INTO ' \
              'CONCEPTS (TITLE, DESCRIPTION) ' \
              'VALUES (%s, %s) ' \
              'RETURNING *'
        params = (concept.title, concept.description)
        return execute_sql_fetch_single(Concept, sql, params)

    def delete_by_id(self, id):
        logger.debug('delete_by_id(): %s', repr(id))

        if id is None or not isinstance(id, LongType):
            raise ObjectCubeException('Function requires valid ID')

        sql = 'DELETE ' \
              'FROM CONCEPTS ' \
              'WHERE ID = %s ' \
              'RETURNING *'
        params = (id,)
        db_concept = execute_sql_fetch_single(Concept, sql, params)

        if db_concept is None:
            raise ObjectCubeException('No concept to delete')
        return None

    def delete(self, concept):
        logger.debug('delete(): %s', repr(concept))

        if concept is None or not isinstance(concept, Concept):
            raise ObjectCubeException('Function requires valid concept')
        if concept.id is None or not isinstance(concept.id, LongType):
            raise ObjectCubeException('Function requires valid ID')

        sql = 'DELETE ' \
              'FROM CONCEPTS ' \
              'WHERE ID = %s ' \
              'RETURNING *'
        params = (concept.id,)
        db_concept = execute_sql_fetch_single(Concept, sql, params)

        if db_concept is None:
            raise ObjectCubeException('No concept to delete')
        return None

    def retrieve_or_create(self, concept):
        logger.debug('retrieve_or_create(): %s', repr(concept))

        if concept is None or not isinstance(concept, Concept):
            raise ObjectCubeException('Function requires valid concept')
        if concept.title is None or not isinstance(concept.title, UnicodeType):
            raise ObjectCubeException('Function requires valid title')

        # Try to retrieve a concept with the title, if found return it
        db_concept = self.retrieve_by_title(concept.title)
        db_concept = self.retrieve_by_title(concept.title)
        if db_concept is not None:
            return db_concept

        # No concept exists, so make sure description is valid and add one
        if concept.description is None:
            concept.description = u''
        return self.add(concept)

    def update(self, concept):
        logger.debug('update(): %s', repr(concept))

        if concept is None or \
                not isinstance(concept, Concept):
            raise ObjectCubeException('Function requires valid concept')
        if concept.id is None or \
                not isinstance(concept.id, LongType):
            raise ObjectCubeException('Function requires valid ID')
        if concept.title is None or \
                not isinstance(concept.title, UnicodeType):
            raise ObjectCubeException('Function requires valid title')
        if concept.description is None or \
                not isinstance(concept.description, UnicodeType):
            raise ObjectCubeException('Function requires valid description')

        sql = 'UPDATE CONCEPTS ' \
              'SET TITLE=%s, DESCRIPTION=%s ' \
              'WHERE ID=%s ' \
              'RETURNING *'
        params = (concept.title, concept.description, concept.id)
        db_concept = execute_sql_fetch_single(Concept, sql, params)

        if not db_concept:
            raise ObjectCubeException('No concept to update')
        return db_concept

    def retrieve_by_id(self, id):
        logger.debug('retrieve_by_id(): %s', repr(id))

        if id is None or not isinstance(id, LongType):
            raise ObjectCubeException('Function requires valid ID')

        sql = 'SELECT * ' \
              'FROM CONCEPTS ' \
              'WHERE ID = %s'
        params = (id,)
        return execute_sql_fetch_single(Concept, sql, params)

    def retrieve_by_title(self, title):
        logger.debug('retrieve_or_create(): %s', repr(title))

        if title is None or not isinstance(title, UnicodeType):
            raise ObjectCubeException('Function requires valid title')

        sql = 'SELECT * ' \
              'FROM CONCEPTS ' \
              'WHERE TITLE = %s'
        params = (title, )
        return execute_sql_fetch_single(Concept, sql, params)

    def retrieve(self, offset=0L, limit=10L):
        logger.debug('retrieve(): %s / %s', repr(offset), repr(limit))

        if offset is None or not isinstance(offset, LongType):
            raise ObjectCubeException('Function requires valid offset')
        if limit is None or not isinstance(limit, LongType):
            raise ObjectCubeException('Function requires valid limit')

        sql = 'SELECT * ' \
              'FROM CONCEPTS ' \
              'OFFSET %s LIMIT %s'
        params = (offset, limit)
        return execute_sql_fetch_multiple(Concept, sql, params)

    def retrieve_by_regex(self, title=None, description=None, offset=0L, limit=10L):
        logger.debug('retrieve_or_create(): %s / %s / %s / %s',
                     repr(title), repr(description), repr(offset), repr(limit))

        if title is not None and not isinstance(title, UnicodeType):
            raise ObjectCubeException('Function requires valid name regex')
        if description is not None and not isinstance(description, UnicodeType):
            raise ObjectCubeException('Function requires valid description regex')
        if title is None and description is None:
            raise ObjectCubeException('Function requires valid at least one valid regex')

        if offset is None or not isinstance(offset, LongType):
            raise ObjectCubeException('Function requires valid offset')
        if limit is None or not isinstance(limit, LongType):
            raise ObjectCubeException('Function requires valid limit')

        if title is not None and description is not None:
            sql = 'SELECT * ' \
                  'FROM CONCEPTS ' \
                  'WHERE TITLE ~ %s ' \
                  '  AND DESCRIPTION ~ %s' \
                  'OFFSET %s LIMIT %s'
            params = (title, description, offset, limit)
        elif description is None:
            sql = 'SELECT * ' \
                  'FROM CONCEPTS ' \
                  'WHERE TITLE ~ %s ' \
                  'OFFSET %s LIMIT %s'
            params = (title, offset, limit)
        else:
            sql = 'SELECT * ' \
                  'FROM CONCEPTS ' \
                  'WHERE DESCRIPTION ~ %s ' \
                  'OFFSET %s LIMIT %s'
            params = (description, offset, limit)
        return execute_sql_fetch_multiple(Concept, sql, params)
