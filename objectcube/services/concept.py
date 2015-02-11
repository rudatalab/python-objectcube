import psycopg2
from objectcube.decorators import with_connection
from objectcube.exceptions import (ObjectCubeDatabaseException,
                                   ObjectCubeException)
from objectcube.services.concept_type import ConceptTypeService
from objectcube.vo import Concept, ConceptType
from objectcube import settings


class ConceptService(object):
    def __init__(self):
        self.concept_type_service = ConceptTypeService()

    @with_connection
    def get_concept_count(self, connection=None):
        """
        Counts number of concepts in the data store.
        :param connection: Connection object to database.
        :return: Number
        :exception ObjectCubeDatabaseException: Any database exception that
        might occur will be wrapped into ObjectCubeDatabaseException.
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(ID) FROM CONCEPTS")
                return cursor.fetchone()[0]
        except Exception as ex:
            raise ObjectCubeDatabaseException(ex)
        finally:
            connection.close()

    @with_connection
    def add_concept(self, concept_type, name, description='', connection=None):
        """
        Adds new concept to data store.
        :param concept_type: Can be id for a given concept type, or ConceptType
        object.
        :param title: Title for the concept.
        :param description: Description of the concept.
        :param connection: Connection object
        :raises: ObjectCubeException of param concept_type is not number or
        ConceptType.
        :raises: ObjectCubeException if concept_type points to invalid, or
        nonexistent Concept type.
        :return: Newly created concept object.
        """
        if not name:
            raise ObjectCubeException('name is required')

        if not description:
            description = ''

        if not isinstance(concept_type, (int, long)) \
                and not isinstance(concept_type, ConceptType):
            raise ObjectCubeException('Parameter concept_type must either '
                                      'be a number or instance of Concept')

        # TODO (hlysig): Write test for this case.
        if isinstance(concept_type, (int, long)):
            concept_type_id = concept_type
            concept_type = \
                self.concept_type_service.get_concept_type_by_id(concept_type)

            if not concept_type:
                raise ObjectCubeException(
                    'No concept type found with id {}'.format(concept_type_id))

        sql = 'INSERT INTO CONCEPTS(NAME, DESCRIPTION, CONCEPT_TYPE_ID) ' \
              'VALUES (%s, %s, %s) RETURNING id'

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, (name, description, concept_type.id))
                concept_id = cursor.fetchone()[0]
                connection.commit()
                return Concept(
                    **{
                        'id': concept_id,
                        'name': name,
                        'description': description,
                        'concept_type_id': concept_type.id
                    }
                )
        except Exception as ex:
            raise ObjectCubeDatabaseException(ex)
        finally:
            connection.close()

    @with_connection
    def get_concepts(self, limit=settings.CONCEPT_SERVICE_DEFAULT_LIMIT,
                     offset=0, connection=None):
        """
        Fetch all concept types that have been added to data store.
        :param limit: Limit for the result fetched from data store. This value
        can be controlled with environment variable
        named OBJECTCUBE_CONCEPT_SERVICE_MAX_LIMIT
        and CONCEPT_SERVICE_MAX_LIMIT
        :param offset: Offset with respect to the limit of the results fetched
        from data store.
        :param connection: Connection object.
        :return: List of Concept objects.
        """
        if offset < 0 or limit < 0:
            raise ObjectCubeException('Offset and limit must be positive')

        # TODO (hlysig): Add tests for this logic.
        # Check if the value for limit is exceeding the configured max limit
        if limit > settings.CONCEPT_SERVICE_MAX_LIMIT:
            raise ObjectCubeException('Requested limit size is greater than '
                                      'configured LIMIT size. Please configure '
                                      'CONCEPT_SERVICE_MAX_LIMIT if needed.')

        return_values = []
        sql = 'SELECT id, name, description, concept_type_id ' \
              'FROM CONCEPTS LIMIT %s OFFSET %s'
        cursor = connection.cursor(
            cursor_factory=psycopg2.extras.NamedTupleCursor)
        cursor.execute(sql, (limit, offset))
        rows = cursor.fetchall()

        for r in rows:
            return_values.append(Concept(**r._asdict()))

        cursor.close()
        connection.close()
        return return_values

    @with_connection
    def get_concept_by_id(self, concept_id, connection=None):
        """
        Fetches concept from data store by id.
        :param concept_id: Id for a given Concept to be fetched from
        data store.
        :param connection: Connection object.
        :return: Concept object if found, None otherwise.
        """
        sql = "SELECT ID, NAME, DESCRIPTION, CONCEPT_TYPE_ID FROM " \
              "CONCEPTS WHERE ID=%s"
        try:
            with connection.cursor(
                    cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
                cursor.execute(sql, (concept_id,))

                row = cursor.fetchone()

                if row:
                    return Concept(**row._asdict())
        except Exception as ex:
            raise ObjectCubeException(ex)
        finally:
            connection.close()

    @with_connection
    def get_concept_by_name(self, name, connection=None):
        """
        Fetches concept from data store by name.
        :param name: Id for a given Concept to be fetched from
        data store.
        :param connection: Connection object.
        :return: Concept object if found, None otherwise.
        """
        sql = "SELECT ID, NAME, DESCRIPTION, CONCEPT_TYPE_ID FROM " \
              "CONCEPTS WHERE NAME=%s"
        try:
            with connection.cursor(
                    cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
                cursor.execute(sql, (name,))

                row = cursor.fetchone()

                if row:
                    return Concept(**row._asdict())
        except Exception as ex:
            raise ObjectCubeDatabaseException(ex)
        finally:
            connection.close()