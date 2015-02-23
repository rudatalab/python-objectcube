from objectcube.services.base import BaseObjectService
from objectcube.contexts import Connection


class FileSystemObjectService(BaseObjectService):
    def add_tag(self, _object, tag_or_tags):
        pass

    def add(self, resource_uri, name):
        sql = 'INSERT INTO OBJECT(NAME, RESOURCE_URI) VALUES(%s, %s) return ID'
        #with Connection() as connection
        #pass

    def count(self):
        pass