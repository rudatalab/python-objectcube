from utils import execute_sql_fetch_single, execute_sql_fetch_multiple
from objectcube.services.base import BaseDimensionService
from objectcube.vo import DimensionNode
from objectcube.exceptions import (ObjectCubeDatabaseException,
                                   ObjectCubeException)
from objectcube.vo import Tag


class DimensionService(BaseDimensionService):

    def _calculate_borders(self, root_node, counter=None):
        if not counter:
            counter = [1];

        root_node.left_border = counter[0]
        counter[0] = counter[0] + 1

        if root_node.child_nodes:
            for node in root_node.child_nodes:
                self._calculate_borders(node, counter)

        root_node.right_border = counter[0]
        counter[0] = counter[0] + 1


    def delete(self, subtree_root_node):
        if not isinstance(subtree_root_node, DimensionNode) or not subtree_root_node.root_tag_id or \
                not subtree_root_node.node_tag_id or not subtree_root_node.left_border or not subtree_root_node.right_border:
            raise ObjectCubeException(
                'Must give DimensionNode with valid root_tag_id, node_tag_id, left_border and right_border')

        sql = 'DELETE FROM DIMENSIONS WHERE root_tag_id = %s AND left_border >= %s AND right_border <= %s RETURNING *'
        params = (subtree_root_node.root_tag_id, subtree_root_node.left_border, subtree_root_node.right_border)
        return execute_sql_fetch_single(DimensionNode, sql, params)

    def add_dimension(self, tag):
        if not isinstance(tag, Tag) or not tag.id :
            raise ObjectCubeException(
                'Must give DimensionNode with valid root_tag_id and node_tag_id')

        root_node = DimensionNode(root_tag_id=tag.id, node_tag_id=tag.id, node_tag_value=tag.value, left_border=0, right_border=0, child_nodes=[]);
        self._calculate_borders(root_node)

        sql = 'INSERT INTO DIMENSIONS(root_tag_id, node_tag_id, left_border, right_border) ' \
              'VALUES(%s, %s, %s, %s) RETURNING *'

        params = (root_node.root_tag_id, root_node.node_tag_id, root_node.left_border, root_node.right_border)
        return execute_sql_fetch_single(DimensionNode, sql, params)

    def retrieve_dimension_by_root(self, root_node):
        if not isinstance(root_node, DimensionNode) or not root_node.root_tag_id or not root_node.node_tag_id or not root_node.root_tag_id == root_node.node_tag_id:
            raise ObjectCubeDatabaseException('Invalid root node')
        sql = 'SELECT D.root_tag_id, D.node_tag_id, T.value, D.left_border, D.right_border' \
                'FROM Dimensions D JOIN Tags T ON D.node_tag_id = T.id' \
                'WHERE D.root_tag_id = %s ORDER BY D.left_border ASC'
        params = (root_node.root_tag_id)
        return _construct_tree(execute_sql_fetch_multiple(DimensionNode, sql, params))

    def _construct_tree(self, dimension_node_array, parent_node=None, counter=None):
        if not counter:
            counter = [0]

        if not parent_node:
            parent_node = dimension_node_array[counter[0]]
            counter[0] = counter[0] + 1

        if counter >= dimension_node_array.size():
            return parent_node

        current_node = dimension_node_array[counter[0]]
        counter[0] = counter[0] + 1

        loop_switch = 1
        while loop_switch == 1:
            if counter[0] >= dimension_node_array.size() or dimension_node_array[counter[0]].right_border > parent_node.right_border:
                return current_node
            parent_node.child_nodes.append(self._construct_tree(dimension_node_array, current_node, counter))

    def _find_node(self, root_node, tag_id):
        if root_node.node_tag_id == tag_id:
            return root_node;
        if not root_node.child_nodes:
            raise ObjectCubeDatabaseException('Tag was not found')
        for node in root_node.child_nodes:
            self._find_node(node, tag_id)

    def _insert_node(self, node):
        sql = 'INSERT INTO DIMENSIONS( ROOT_TAG_ID, NODE_TAG_ID, LEFT_BORDER, RIGHT_BORDER) VALUES( %s, %s, %s, %s)'
        params = (node.root_tag_id, node.node_tag_id, node.left_border, node.right_border)
        execute_sql_fetch_single(DimensionNode, sql, params)

    def _write_nodes(self, root_node):
        self._insert_node(root_node)
        for child in root_node.child_nodes:
            self._write_nodes(child)

    def add_node(self, parent_node, tag):
        if not isinstance(parent_node, DimensionNode) or not isinstance(tag, Tag):
            raise ObjectCubeDatabaseException('Input not of correct types')

        root_node = self.retrieve_dimension_by_root(DimensionNode(root_tag_id=parent_node.root_tag_id))
        revised_parent_node = self._find_node(root_node, tag.id)
        revised_parent_node.child_nodes.append(child_node)
        self._calculate_borders(root_node)
        self.delete(root_node)
        self._write_nodes(root_node)

    def retrieve_by_tag(self, root_node, tag):
        pass

    def print_tree(self, root_node, indent=''):
        print 'id=', root_node.root_tag_id,'L=',root_node.left_border,' R=',root_node.right_border
        if not root_node.child_nodes:
            return
        for node in root_node.child_nodes:
            self.print_tree(node, indent + '  ')


'''
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
'''