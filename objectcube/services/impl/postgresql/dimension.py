from json import dumps, loads
from psycopg2.extras import NamedTupleCursor
from objectcube.vo import Tree
from objectcube.services.base import BaseDimensionService
from objectcube.contexts import Connection
from objectcube.exceptions import (ObjectCubeException,
                                   ObjectCubeDatabaseException)


class DimensionServicePostgreSQL(BaseDimensionService):
    def get_dimensions(self, offset=0, limit=100):
        return_list = []

        sql = 'SELECT TREE FROM DIMENSIONS LIMIT %s OFFSET %s'
        try:
            with Connection() as c:
                with c.cursor(cursor_factory=NamedTupleCursor) as cursor:
                    cursor.execute(sql, (limit, offset))

                    for tree_string in cursor.fetchall():
                        des = Tree.deserialize_tree(loads(*tree_string))
                        return_list.append(des)
        except Exception as ex:
            raise ObjectCubeDatabaseException(ex)

        return return_list

    def get_by_id(self, _id):
        if not _id or _id <= 0 or not isinstance(_id, int):
            raise ObjectCubeException('ID must be a positive integer')

        sql = "SELECT TREE FROM DIMENSIONS WHERE ID = {}".format(_id)

        try:
            with Connection() as c:
                with c.cursor(cursor_factory=NamedTupleCursor) as cursor:
                    cursor.execute(sql)
                    tree_string = cursor.fetchone()
                    if tree_string:
                        return Tree.deserialize_tree(loads(*tree_string))
        except Exception as e:
            raise ObjectCubeDatabaseException(e)

    def get_by_name(self, name):
        # TODO: Get confirmation if names of dimensions have to be unique
        # Otherwise possibly implement get_by_value
        if not name or name == '' or not isinstance(name, basestring):
            raise ObjectCubeException('NAME must be a nonempty string')

        sql = "SELECT TREE FROM DIMENSIONS WHERE NAME = '{0}'".format(name)

        try:
            with Connection() as c:
                with c.cursor(cursor_factory=NamedTupleCursor) as cursor:
                    cursor.execute(sql)
                    tree_string = cursor.fetchone()
                    if tree_string:
                        return Tree.deserialize_tree(loads(*tree_string))
        except Exception as e:
            raise ObjectCubeDatabaseException(e)

    def add_dimension(self, tree):
        sql = 'INSERT INTO DIMENSIONS(NAME, TREE) VALUES(%s, %s) RETURNING ID'

        try:
            with Connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, (tree.name, dumps(tree.serialize())))
                    tree.id = cursor.fetchone()[0]
                    connection.commit()
        except Exception as ex:
            raise ObjectCubeDatabaseException(ex)

    def update_dimension(self, name, new_tree):
        if not name or name == '' or not isinstance(new_tree, Tree):
            raise ObjectCubeException('Updating requires a non empty name '
                                      'and a replacement tree')

        sql = "UPDATE DIMENSIONS SET TREE=%s WHERE NAME=%s"

        try:
            with Connection() as c:
                with c.cursor() as cursor:
                    cursor.execute(sql, (dumps(new_tree.serialize()), name))
        except Exception as ex:
            raise ObjectCubeDatabaseException(ex)
