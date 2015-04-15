import unittest
from objectcube.db import create_connection
from objectcube.vo import Concept, Plugin, Tag


class TestDatabaseAwareTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestDatabaseAwareTest, self).__init__(*args, **kwargs)

    def setUp(self):
        with open('schema.sql') as fd:
            data = ''.join(fd.readlines())

        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(data)

            connection.commit()


class ObjectCubeTestCase(TestDatabaseAwareTest):

    def __init__(self, *args, **kwargs):
        super(ObjectCubeTestCase, self).__init__(*args, **kwargs)

    def _create_test_tag(self, value='', plugin=Plugin(), concept=Concept()):
        """
        Helper function for creating test tags in tests.
        :param value: Value for the tag being created
        :return: Tag instance that can be added to data store.
        """
        return Tag(**{
            'id': None,
            'value': value,
            'description': '',
            'mutable': False,
            'type': 0,
            'concept_id': concept.id,
            'plugin_id': plugin.id,
        })
