import unittest
from objectcube.contexts import Connection


class TestDatabaseAwareTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestDatabaseAwareTest, self).__init__(*args, **kwargs)

    def setUp(self):
        with open('schema.sql') as fd:
            data = ''.join(fd.readlines())

        with Connection() as c:
            with c.cursor() as cursor:
                cursor.execute(data)


class ObjectCubeTestCase(TestDatabaseAwareTest):

    def __init__(self, *args, **kwargs):
        super(ObjectCubeTestCase, self).__init__(*args, **kwargs)

    # def _create_test_tag(self, value=u'Value', description=u'Description',
    #                      plugin=None, concept=None):
    #     """
    #     Helper function for creating test tags in tests.
    #     :param value: Value for the tag being created
    #     :return: Tag instance that can be added to data store.
    #     """
    #     return Tag(**{
    #         'id': None,
    #         'value': value,
    #         'description': description,
    #         'mutable': False,
    #         'type': 0L,
    #         'concept_id': concept.id if concept is not None else None,
    #         'plugin_id': plugin.id if plugin is not None else None,
    #     })
    #
