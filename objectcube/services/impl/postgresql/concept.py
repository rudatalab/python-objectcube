from utils import execute_sql_fetch_single, execute_sql_fetch_multiple
from objectcube.data_objects import Concept
from objectcube.exceptions import ObjectCubeException
from objectcube.services.base import BaseConceptService
from types import LongType, UnicodeType, NoneType
from logging import getLogger


class ConceptService(BaseConceptService):
    def __init__(self):
        super(ConceptService, self).__init__()
        self.logger = getLogger('postgreSQL: ConceptService')

    def count(self):
        self.logger.debug('count()')
        sql = 'SELECT COUNT(1) AS count ' \
              'FROM CONCEPTS'
        return execute_sql_fetch_single(lambda count: count, sql)

    def add(self, concept):
        self.logger.debug('add(): %s', repr(concept))

        if not isinstance(concept, Concept):
            raise ObjectCubeException('Function requires valid concept')
        if concept.id:
            raise ObjectCubeException('Function must not get id')

        sql = 'INSERT INTO ' \
              'CONCEPTS (TITLE, DESCRIPTION) ' \
              'VALUES (%s, %s) ' \
              'RETURNING *'
        params = (concept.title, concept.description)
        return execute_sql_fetch_single(Concept, sql, params)

    def delete_by_id(self, id_):
        self.logger.debug('delete_by_id(): %s', repr(id_))

        if not isinstance(id_, LongType):
            raise ObjectCubeException('Function requires valid id')

        sql = 'DELETE ' \
              'FROM CONCEPTS ' \
              'WHERE ID = %s ' \
              'RETURNING *'
        params = (id_,)
        db_concept = execute_sql_fetch_single(Concept, sql, params)

        if not db_concept:
            raise ObjectCubeException('No Concept found to delete')
        return None

    def delete(self, concept):
        self.logger.debug('delete(): %s', repr(concept))

        if not isinstance(concept, Concept):
            raise ObjectCubeException('Function requires valid Concept')
        if not concept.id:
            raise ObjectCubeException('Function requires valid Concept id')

        sql = 'DELETE ' \
              'FROM CONCEPTS ' \
              'WHERE ID = %s ' \
              'RETURNING *'
        params = (concept.id,)
        db_concept = execute_sql_fetch_single(Concept, sql, params)

        if not db_concept:
            raise ObjectCubeException('No Concept found to delete')
        return None

    def retrieve_or_create(self, concept):
        self.logger.debug('retrieve_or_create(): %s', repr(concept))

        if not isinstance(concept, Concept):
            raise ObjectCubeException('Function requires valid Concept')

        # Try to retrieve a concept with the title
        db_concept = self.retrieve_by_title(concept.title)

        # If concept was found return it, otherwise add and return
        if db_concept:
            return db_concept
        else:
            return self.add(concept)

    def update(self, concept):
        self.logger.debug('update(): %s', repr(concept))

        if not isinstance(concept, Concept):
            raise ObjectCubeException('Function requires valid Concept')
        if not concept.id:
            raise ObjectCubeException('Function requires valid Concept id')

        sql = 'UPDATE CONCEPTS ' \
              'SET TITLE=%s, DESCRIPTION=%s ' \
              'WHERE ID=%s ' \
              'RETURNING *'
        params = (concept.title, concept.description, concept.id)
        db_concept = execute_sql_fetch_single(Concept, sql, params)

        if not db_concept:
            raise ObjectCubeException('No Concept found to update')
        return db_concept

    def retrieve_by_id(self, id_):
        self.logger.debug('retrieve_by_id(): %s', repr(id_))

        if not isinstance(id_, LongType):
            raise ObjectCubeException('Function requires valid id')

        sql = 'SELECT * ' \
              'FROM CONCEPTS ' \
              'WHERE ID = %s'
        params = (id_,)
        return execute_sql_fetch_single(Concept, sql, params)

    def retrieve_by_title(self, title):
        self.logger.debug('retrieve_or_create(): %s', repr(title))

        if not isinstance(title, UnicodeType):
            raise ObjectCubeException('Function requires valid title')

        sql = 'SELECT * ' \
              'FROM CONCEPTS ' \
              'WHERE TITLE = %s'
        params = (title, )
        return execute_sql_fetch_single(Concept, sql, params)

    def retrieve(self, offset=0L, limit=10L):
        self.logger.debug('retrieve(): %s / %s', repr(offset), repr(limit))

        if not isinstance(offset, LongType):
            raise ObjectCubeException('Function requires valid offset')
        if not isinstance(limit, LongType):
            raise ObjectCubeException('Function requires valid limit')

        sql = 'SELECT * ' \
              'FROM CONCEPTS ' \
              'OFFSET %s LIMIT %s'
        params = (offset, limit)
        return execute_sql_fetch_multiple(Concept, sql, params)

    def retrieve_by_regex(self, title=None, description=None,
                          offset=0L, limit=10L):
        self.logger.debug('retrieve_or_create(): %s / %s / %s / %s',
                          repr(title), repr(description),
                          repr(offset), repr(limit))

        if not isinstance(title, (UnicodeType, NoneType)):
            raise ObjectCubeException('Function requires valid name regex')
        if not isinstance(description, (UnicodeType, NoneType)):
            raise ObjectCubeException('Function requires valid desc regex')
        if not title and not description:
            raise ObjectCubeException('Function requires one valid regex')

        if offset is None or not isinstance(offset, LongType):
            raise ObjectCubeException('Function requires valid offset')
        if limit is None or not isinstance(limit, LongType):
            raise ObjectCubeException('Function requires valid limit')

        if title and description:
            sql = 'SELECT * ' \
                  'FROM CONCEPTS ' \
                  'WHERE TITLE ~ %s ' \
                  '  AND DESCRIPTION ~ %s' \
                  'OFFSET %s LIMIT %s'
            params = (title, description, offset, limit)
        elif title:
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
