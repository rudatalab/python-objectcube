import logging

from objectcube.vo import Concept
from utils import execute_sql_fetch_single, execute_sql_fetch_multiple
from objectcube.exceptions import ObjectCubeException
from objectcube.services.base import BaseConceptService
from types import IntType, StringType

logger = logging.getLogger('PostgreSQL:ConceptService')


class ConceptService(BaseConceptService):
    def count(self):
        logger.debug('count()')
        sql = 'SELECT COUNT(1) AS count FROM CONCEPTS'
        return execute_sql_fetch_single(lambda count: count, sql)

    def add(self, concept):
        logger.debug('add(): %s', repr(concept))

        if concept is None or not isinstance(concept, Concept):
            raise ObjectCubeException('Add requires a valid concept')
        if not concept.id is None:
            raise ObjectCubeException('Add must not get ID')
        if not concept.title or not isinstance(concept.title, StringType):
            raise ObjectCubeException('Unable to add concept without a valid title')
        if not concept.description or not isinstance(concept.description, StringType):
            raise ObjectCubeException('Unable to add concept without a valid description')

        sql = 'INSERT INTO ' \
              'CONCEPTS(TITLE, DESCRIPTION) ' \
              'VALUES(%s, %s) ' \
              'RETURNING *'
        params = (concept.title, concept.description)
        db_concept = execute_sql_fetch_single(Concept, sql, params)

        if db_concept is None:
            raise ObjectCubeException('No concept added with value {}'.format(concept.value))
        return db_concept

    def delete_by_id(self, concept_id):
        logger.debug('delete_by_id(): %s', repr(concept_id))

        if concept_id is None or not isinstance(concept_id, IntType):
            raise ObjectCubeException('Unable to find concept to delete without id')

        sql = 'DELETE ' \
              'FROM CONCEPTS ' \
              'WHERE ID = %s ' \
              'RETURNING *'
        params = (concept_id,)
        concept = execute_sql_fetch_single(Concept, sql, params)

        if concept is None:
            raise ObjectCubeException('No concept found with id {}'.format(concept_id))
        return None

    def delete(self, concept):
        logger.debug('delete(): %s', repr(concept))

        if concept is None or not isinstance(concept, Concept):
            raise ObjectCubeException('Delete accepts only Concept objects')
        if concept.id is None or not isinstance(concept.id, IntType):
            raise ObjectCubeException('Delete accepts only Concept objects with valid ID')

        self.delete_by_id(concept.id)

    def retrieve_or_create(self, concept):
        logger.debug('retrieve_or_create(): %s', repr(concept))

        if type(concept) != Concept:
            raise ObjectCubeException('retrieve_or_create accepts only Concept objects')

        db_concept = self.retrieve_by_title(concept.title)
        if db_concept:
            return db_concept

        return self.add(concept)

    def update(self, concept):
        logger.debug('update(): %s', repr(concept))

        if concept is None or not isinstance(concept, Concept):
            raise ObjectCubeException('Unable to update concept without id')
        if concept.id is None or not isinstance(concept.id, IntType):
            raise ObjectCubeException('Unable to update concept without id')
        if not concept.title or not isinstance(concept.title, StringType):
            raise ObjectCubeException('Unable to update concept without a valid title')
        if not concept.description or not isinstance(concept.description, StringType):
            raise ObjectCubeException('Unable to update concept without a valid description')

        sql = 'UPDATE CONCEPTS ' \
              'SET TITLE=%s, DESCRIPTION=%s ' \
              'WHERE ID=%s ' \
              'RETURNING *'
        params = (concept.title, concept.description, concept.id)
        db_concept = execute_sql_fetch_single(Concept, sql, params)

        if not db_concept:
            raise ObjectCubeException('No concept found with id {}'.format(concept.id))
        return db_concept

    def retrieve_by_title(self, concept_title):
        logger.debug('retrieve_or_create(): %s', repr(concept_title))

        if not concept_title or not isinstance(concept_title, StringType):
            raise ObjectCubeException('Unable to add concept without a valid title')

        sql = "SELECT * " \
              "FROM CONCEPTS " \
              "WHERE TITLE = %s"
        params = (concept_title,)
        return execute_sql_fetch_single(Concept, sql, params)

    def retrieve_by_id(self, concept_id):
        logger.debug('retrieve_by_id(): %s', repr(concept_id))

        if not concept_id or not isinstance(concept_id, IntType):
            raise ObjectCubeException('Must provide concept_id')

        sql = "SELECT * " \
              "FROM CONCEPTS " \
              "WHERE ID = %s"
        params = (concept_id,)
        return execute_sql_fetch_single(Concept, sql, params)

    def retrieve(self, offset=0, limit=10):
        logger.debug('retrieve()')

        sql = "SELECT * " \
              "FROM CONCEPTS " \
              "OFFSET %s LIMIT %s"
        params = (offset, limit)
        return execute_sql_fetch_multiple(Concept, sql, params)
