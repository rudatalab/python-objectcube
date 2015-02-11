import unittest
from objectcube.db import create_connection


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