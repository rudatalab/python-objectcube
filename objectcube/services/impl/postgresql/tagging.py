from psycopg2.extras import NamedTupleCursor

from utils import execute_sql_fetch_single
from objectcube.services.base import BaseTaggingService
from objectcube.contexts import Connection
from objectcube.vo import Object, Plugin, Tag, Tagging
from objectcube.exceptions import ObjectCubeException


class TaggingService(BaseTaggingService):

    def add(self,object, tag, meta, plugin=Plugin(), plugin_set_id=None):
        if not isinstance(object, Object) or not object.id:
            raise ObjectCubeException('Must give object with valid id')
        if not isinstance(tag, Tag) or not tag.id:
            raise ObjectCubeException('Must give tag with valid id')
        if not isinstance(plugin, Plugin):
            raise ObjectCubeException('Must give plugin')

        sql = 'INSERT INTO OBJECT_TAG(OBJECT_ID, TAG_ID) values (%s, %s) RETURNING *'
        params = (object.id, tag.id)

        return execute_sql_fetch_single(Tagging, sql, params)

    def delete_by_set_id(self,plugin_set_id):
        raise NotImplementedError()

    def resolve(self,object, tag, meta, plugin=Plugin(), plugin_set_id=None):
        raise NotImplementedError()

    def delete(self,tagging):
        raise NotImplementedError()

    def update(self,tagging):
        raise NotImplementedError()
