import psycopg2
import psycopg2.extras

from objectcube.decorators import with_connection
from objectcube.vo import ConceptType
from objectcube.exceptions import (ObjectCubeDatabaseException,
                                   ObjectCubeException)


class ConceptTypeService(object):
    @with_connection
    def get_concept_types(self, connection=None):
        """
        Fetch all concept types that have been added to data store.
        :param connection: Connection object to database.
        :return: List of ConceptType objects.
        """
        return_values = []
        sql = 'SELECT id, name, concept_base_type, regex_pattern ' \
              'FROM CONCEPT_TYPE'
        cursor = connection.cursor(
            cursor_factory=psycopg2.extras.NamedTupleCursor)
        cursor.execute(sql)
        rows = cursor.fetchall()

        for r in rows:
            return_values.append(ConceptType(**r._asdict()))

        cursor.close()
        connection.close()
        return return_values

    @with_connection
    def add_concept_type(self, name, regex_pattern='', concept_base_type=None,
                         connection=None):
        """
        Adds new concept type to data store.
        :param name: Name of the concept
        :param regex: Regex that concept instance must follow to be
        part of this concept type. Note that this field is optional.
        :param connection: Database connection object
        :return: Id of the last inserted concept type.
        """

        if not concept_base_type:
            concept_base_type = ConceptType.default_type
        else:
            if concept_base_type not in ConceptType.allowed_types:
                raise ObjectCubeException('Invalid concept type')

        if concept_base_type != 'REGEX' and regex_pattern:
            raise ObjectCubeException('Regex parameter is only allowed when '
                                      'we have base type of type REGEX')

        try:
            with connection.cursor() as cursor:

                cursor.execute("insert into CONCEPT_TYPE "
                               "(name, regex_pattern, concept_base_type) "
                               "values (%s, %s, %s) RETURNING id",
                               (name, regex_pattern, concept_base_type))

                connection.commit()
                return ConceptType(**{
                    'id': cursor.fetchone()[0],
                    'name': name,
                    'regex_pattern': regex_pattern,
                    'concept_base_type': concept_base_type})

        except Exception as ex:
            raise ObjectCubeDatabaseException(ex)
        finally:
            connection.close()

    @with_connection
    def get_concept_type_count(self, connection=None):
        try:
            sql = "select count(id) from CONCEPT_TYPE"
            count = 0
            with connection.cursor() as cursor:
                cursor.execute(sql)
                row = cursor.fetchone()
                cursor.close()
                count = row[0]
            connection.close()
            return count
        except Exception as ex:
            raise ObjectCubeDatabaseException(ex)
        finally:
            connection.close()

    @with_connection
    def get_concept_type_by_id(self, concept_type_id, connection=None):
        """
        :param concept_type_id:
        :param connection:
        :return:
        """
        sql = "SELECT ID, NAME, REGEX_PATTERN, CONCEPT_BASE_TYPE FROM " \
              "CONCEPT_TYPE WHERE ID=%s"
        try:
            with connection.cursor(
                    cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
                cursor.execute(sql, (concept_type_id,))

                row = cursor.fetchone()

                if row:
                    return ConceptType(**row._asdict())
        except Exception as ex:
            raise ObjectCubeDatabaseException(ex)
        finally:
            connection.close()

    @with_connection
    def get_concept_type_by_name(self, name, connection=None):
        """

        :param name:
        :param connection:
        :return:
        """
        sql = "SELECT ID, NAME, REGEX_PATTERN FROM CONCEPT_TYPE WHERE NAME=%s"

        try:
            with connection.cursor(
                    cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
                cursor.execute(sql, (name,))

                row = cursor.fetchone()

                if row:
                    return ConceptType(**row._asdict())
        except Exception as ex:
            raise ObjectCubeDatabaseException(ex)
        finally:
            connection.close()

    def delete_concept(self, id):
        raise Exception('Not implemented')
