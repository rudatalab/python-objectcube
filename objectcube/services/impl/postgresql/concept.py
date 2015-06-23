import logging

from objectcube.vo import Concept
from utils import execute_sql_fetch_single, execute_sql_fetch_multiple
from objectcube.exceptions import ObjectCubeException
from objectcube.services.base import BaseConceptService
from types import IntType, LongType, StringType, UnicodeType

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
        if concept.title is None or not isinstance(concept.title, (StringType, UnicodeType)):
            raise ObjectCubeException('Function requires valid title')
        if concept.description is None or not isinstance(concept.description, (StringType, UnicodeType)):
            raise ObjectCubeException('Function requires valid description')
        if concept.id is not    None:
            raise ObjectCubeException('Function must not get ID')

        sql = 'INSERT INTO ' \
              'CONCEPTS (TITLE, DESCRIPTION) ' \
              'VALUES (%s, %s) ' \
              'RETURNING *'
        params = (concept.title, concept.description)
        return execute_sql_fetch_single(Concept, sql, params)

    def delete_by_id(self, id):
        logger.debug('delete_by_id(): %s', repr(id))

        if id is None or not isinstance(id, (IntType, LongType)):
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
        if concept.id is None or not isinstance(concept.id, (IntType, LongType)):
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
        if concept.title is None or not isinstance(concept.title, (StringType, UnicodeType)):
            raise ObjectCubeException('Function requires valid title')

        # Try to retrieve a concept with the title, if found return it
        db_concept = self.retrieve_by_title(concept.title)
        if db_concept is not None:
            return db_concept

        # No concept exists, so make sure description is valid and add one
        if concept.description is None:
            concept.description = ''
        return self.add(concept)

    def update(self, concept):
        logger.debug('update(): %s', repr(concept))

        if concept is None or \
                not isinstance(concept, Concept):
            raise ObjectCubeException('Function requires valid concept')
        if concept.id is None or \
                not isinstance(concept.id, (IntType, LongType)):
            raise ObjectCubeException('Function requires valid ID')
        if concept.title is None or \
                not isinstance(concept.title, (StringType, UnicodeType)):
            raise ObjectCubeException('Function requires valid title')
        if concept.description is None or \
                not isinstance(concept.description, (StringType, UnicodeType)):
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

        if id is None or not isinstance(id, (IntType, LongType)):
            raise ObjectCubeException('Function requires valid ID')

        sql = 'SELECT * ' \
              'FROM CONCEPTS ' \
              'WHERE ID = %s'
        params = (id,)
        return execute_sql_fetch_single(Concept, sql, params)

    def retrieve_by_title(self, title):
        logger.debug('retrieve_or_create(): %s', repr(title))

        if title is None or not isinstance(title, (StringType, UnicodeType)):
            raise ObjectCubeException('Function requires valid title')

        sql = 'SELECT * ' \
              'FROM CONCEPTS ' \
              'WHERE TITLE = %s'
        params = (title, )
        return execute_sql_fetch_single(Concept, sql, params)

    def retrieve(self, offset=0, limit=10):
        logger.debug('retrieve()')

        if offset is None or not isinstance(offset, (IntType, LongType)):
            raise ObjectCubeException('Function requires valid offset')
        if limit is None or not isinstance(limit, (IntType, LongType)):
            raise ObjectCubeException('Function requires valid limit')

        sql = 'SELECT * ' \
              'FROM CONCEPTS ' \
              'OFFSET %s LIMIT %s'
        params = (offset, limit)
        return execute_sql_fetch_multiple(Concept, sql, params)

    def retrieve_by_regex(self, regex, offset=0, limit=10):
        logger.debug('retrieve_or_create(): %s', repr(regex))

        if regex is None or not isinstance(regex, (StringType, UnicodeType)):
            raise ObjectCubeException('Function requires valid title')
        if offset is None or not isinstance(offset, (IntType, LongType)):
            raise ObjectCubeException('Function requires valid offset')
        if limit is None or not isinstance(limit, (IntType, LongType)):
            raise ObjectCubeException('Function requires valid limit')

        sql = 'SELECT * ' \
              'FROM CONCEPTS ' \
              'WHERE TITLE ~ %s ' \
              'OFFSET %s LIMIT %s'
        params = (regex, offset, limit)
        return execute_sql_fetch_multiple(Concept, sql, params)
