import hashlib

from objectcube.services.base import BaseObjectService
from objectcube.contexts import Connection
from objectcube.exceptions import ObjectCubeDatabaseException


def md5_for_file(f, block_size=2**20):
    f.seek(0)
    md5 = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)
    f.seek(0)
    return md5.hexdigest()


class ObjectService(BaseObjectService):
    def count(self):
        sql = """SELECT COUNT(ID) FROM OBJECTS"""
        try:
            with Connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql)
                    row = cursor.fetchone()
                    return int(row[0])
        except Exception as ex:
            raise ObjectCubeDatabaseException(ex)

    def add_tag(self, _object, tag_or_tags):
        pass

    def add(self, stream, name):
        file_digest = md5_for_file(stream)
        sql = 'INSERT INTO OBJECTS(NAME, DIGEST) values (%s, %s) RETURNING ID'

        try:
            with Connection() as connection:
                cursor = connection.cursor()
                cursor.execute(sql, (name, file_digest))
                row = cursor.fetchone()
                return int(row[0])

        except Exception as ex:
            raise ObjectCubeDatabaseException(ex)


