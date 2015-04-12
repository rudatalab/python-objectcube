import logging
from psycopg2.extras import NamedTupleCursor

from objectcube.contexts import Connection
from objectcube.vo import Concept
from objectcube.exceptions import (ObjectCubeDatabaseException,
                                   ObjectCubeException)
from objectcube.services.base import BaseConceptService

logger = logging.getLogger('PostgreSQL:ConceptService')


class ConceptService(BaseConceptService):
    def delete_by_id(self, concept_id):
        if not(type(concept_id) == int and concept_id > 0):
            message = 'Unable to update concept without id'
            logger.error(message)
            raise ObjectCubeException(message)

        logger.debug("Calling delete_by_id on concept {}".format(concept_id))

        sql = 'DELETE FROM CONCEPTS WHERE ID = %s RETURNING *'
        params = (concept_id,)
        concept = self._execute_single_concept_sql(sql, params)
        if not concept:
            raise ObjectCubeException('No concept found with id {}'
                                      .format(concept_id))

    def delete(self, concept):
        if type(concept) != Concept:
            message = 'Delete accepts only Concept objects'
            logger.error(message)
            raise ObjectCubeException(message)

        logger.debug('Calling delete on concept {}'.format(repr(concept)))
        self.delete_by_id(concept.id)

    def retrieve_or_create(self, concept):
        db_concept = self.retrieve_by_title(concept.title)
        if db_concept:
            return db_concept

        return self.add(concept)

    def update(self, concept):
        if not concept.id:
            message = 'Unable to update concept without id'
            logger.error(message)
            raise ObjectCubeException(message)

        if not concept.title:
            message = 'Unable to update concept without a title'
            logger.error(message)
            raise ObjectCubeException(message)

        logger.debug("Calling update on concept {}".format(repr(concept)))

        sql = 'UPDATE CONCEPTS SET TITLE=%s, DESCRIPTION=%s WHERE ID=%s ' \
              'RETURNING *'
        params = (concept.title, concept.description, concept.id)
        db_concept = self._execute_single_concept_sql(sql, params)

        if not db_concept:
            raise ObjectCubeException('No concept found with id {}'
                                      .format(concept.id))
        return db_concept

    def count(self):
        logger.debug('Calling count')
        sql = """SELECT COUNT(ID) FROM CONCEPTS"""
        try:
            with Connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql)
                    row = cursor.fetchone()
                    return int(row[0])
        except Exception as ex:
            logger.error(ex.message)
            raise ObjectCubeDatabaseException(ex)

    def add(self, concept):
        logger.debug('Calling add')
        if concept.id:
            message = 'Unable to to concept with id'
            logger.error(message)
            raise ObjectCubeException(message)

        if not concept.title:
            message = 'Unable to to concept with without a title'
            logger.error(message)
            raise ObjectCubeException(message)

        sql = 'INSERT INTO CONCEPTS(TITLE, DESCRIPTION) ' \
              'VALUES(%s, %s) RETURNING *'

        params = (concept.title, concept.description)
        return self._execute_single_concept_sql(sql, params)

    @staticmethod
    def _execute_single_concept_sql(sql, params, commit=True):
        try:
            with Connection() as c:
                with c.cursor(cursor_factory=NamedTupleCursor) as cursor:
                    cursor.execute(sql, params)
                    row = cursor.fetchone()
                    if commit:
                        c.commit()
                    if row:
                        return Concept(**row._asdict())
        except Exception as ex:
            logger.error(ex.message)
            raise ObjectCubeDatabaseException(ex)

    def retrieve_by_title(self, concept_title):
        if not concept_title:
            message = 'Missing title'
            logger.error(message)
            raise ObjectCubeException(message)

        sql = "SELECT * FROM CONCEPTS WHERE TITLE = %s"
        params = (concept_title,)
        return self._execute_single_concept_sql(sql, params, commit=False)

    def retrieve_by_id(self, concept_id):
        if not concept_id:
            message = 'Missing concept_id'
            logger.error(message)
            raise ObjectCubeException(message)

        sql = "SELECT * FROM CONCEPTS WHERE ID = %s"
        params = (concept_id,)
        return self._execute_single_concept_sql(sql, params, commit=False)

    @staticmethod
    def _retrieve_multiple_tags(sql, params):
        try:
            with Connection() as c:
                with c.cursor(cursor_factory=NamedTupleCursor) as cursor:
                    cursor.execute(sql, params)

                    return_list = []
                    for row in cursor.fetchall():
                        return_list.append(Concept(**row._asdict()))
                    return return_list
        except Exception as e:
            raise ObjectCubeDatabaseException(e)

    def retrieve(self, offset=0, limit=100):
        # TODO (hlysig) check if limit and offsset are correct.
        sql = "SELECT * FROM CONCEPTS OFFSET %s LIMIT %s"
        params = (offset, limit)
        return self._retrieve_multiple_tags(sql, params)

