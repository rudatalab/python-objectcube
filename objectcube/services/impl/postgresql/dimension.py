from utils import execute_sql_fetch_single, execute_sql_fetch_multiple
from types import IntType
from objectcube.services.base import BaseDimensionService
from objectcube.exceptions import (ObjectCubeDatabaseException,
                                   ObjectCubeException)
from objectcube.vo import (Tag, DimensionNode)


class DimensionService(BaseDimensionService):
    def _calculate_borders(self, root_node, counter=None):
        # Input: Root node of a valid tree structure
        # Output: Nothing
        # Side effect: The left_border and right_border values are correct in the input tree
        if not counter:
            counter = [1]

        root_node.left_border = counter[0]
        counter[0] += 1

        if root_node.child_nodes:
            for node in root_node.child_nodes:
                self._calculate_borders(node, counter)

        root_node.right_border = counter[0]
        counter[0] += 1

    def _construct_tree(self, dimension_node_array, counter=None):
        # Input: Array of nodes representing a valid tree structure, without any linking
        # Output: The root node of a valid tree structure
        if not counter:
            counter = [0]

        parent_node = DimensionNode(root_tag_id=dimension_node_array[counter[0]].root_tag_id,
                                    node_tag_id=dimension_node_array[counter[0]].node_tag_id,
                                    node_tag_value=dimension_node_array[counter[0]].node_tag_value,
                                    left_border=dimension_node_array[counter[0]].left_border,
                                    right_border=dimension_node_array[counter[0]].right_border,
                                    child_nodes=[])
        counter[0] += 1

        while True:
            if counter[0] >= len(dimension_node_array) \
                    or dimension_node_array[counter[0]].right_border > parent_node.right_border:
                return parent_node
            parent_node.child_nodes.append(self._construct_tree(dimension_node_array, counter))

    def _find_node(self, root_node, tag_id):
        # Input: The root node of a valid tree structure, a tag
        # Output: The node of the tree that contains the tag, None otherwise
        if root_node.node_tag_id == tag_id:
            return root_node

        for node in root_node.child_nodes:
            return_node = self._find_node(node, tag_id)
            if return_node is not None:
                return return_node
        return None

    def _insert_node(self, node):
        # Input: A single tree node
        # Side effect: The tree node has been written to the database
        # Output: The Node written
        sql = 'INSERT INTO DIMENSIONS( ROOT_TAG_ID, NODE_TAG_ID, LEFT_BORDER, RIGHT_BORDER) ' \
              'VALUES( %s, %s, %s, %s) RETURNING *'
        params = (node.root_tag_id, node.node_tag_id, node.left_border, node.right_border)
        return execute_sql_fetch_single(DimensionNode, sql, params)

    def _write_nodes(self, root_node):
        # Input: The root node of a valid tree structure
        # Side effect: The tree has been written to the database
        # Output: The root node
        self._insert_node(root_node)
        for child in root_node.child_nodes:
            self._write_nodes(child)
        return root_node

    def _read_nodes(self, root_node):
        # Input: A valid root node
        # Output: The root node of a valid tree structure
        sql = ('        SELECT D.root_tag_id, D.node_tag_id, T.value, D.left_border, D.right_border '
               '        FROM Dimensions D JOIN Tags T ON D.node_tag_id = T.id '
               '        WHERE D.root_tag_id = %s ORDER BY D.left_border ASC')
        params = (root_node.root_tag_id,)
        return self._construct_tree(execute_sql_fetch_multiple(DimensionNode, sql, params))

    def _read_roots(self, tag=None):
        # Input: An optional tag
        # Output: An array of all the root nodes (of dimensions that contain the tag)
        if tag is not None:
            sql = 'SELECT D1.root_tag_id, D1.node_tag_id, T1.value, D1.left_border, D1.right_border ' \
                  'FROM Dimensions D1 ' \
                  '  JOIN Dimensions D2 ON D1.root_tag_id = D2.root_tag_id ' \
                  '  JOIN Tags T1 ON D1.node_tag_id = T1.id ' \
                  '  JOIN Tags T2 ON D2.node_tag_id = T2.id ' \
                  'WHERE D1.root_tag_id = D1.node_tag_id AND T2.value = %s::text ' \
                  'ORDER BY D1.left_border ASC'
            params = (tag.value,)
        else:
            sql = ('        SELECT D.root_tag_id, D.node_tag_id, T.value, D.left_border, D.right_border '
                   '        FROM Dimensions D JOIN Tags T ON D.node_tag_id = T.id '
                   '        WHERE D.root_tag_id = D.node_tag_id ORDER BY D.left_border ASC')
            params = None
        return execute_sql_fetch_multiple(DimensionNode, sql, params)

    def _delete(self, subtree_root_node):
        # Input: The root node of a valid sub-tree structure
        # Side effect: The sub-tree has been deleted from the database
        # Output: None
        sql = 'DELETE FROM DIMENSIONS WHERE root_tag_id = %s AND left_border >= %s AND right_border <= %s RETURNING *'
        params = (subtree_root_node.root_tag_id, subtree_root_node.left_border, subtree_root_node.right_border)
        execute_sql_fetch_single(DimensionNode, sql, params)
        return None

    def count(self):
        # Input: None
        # Output: The count of valid dimensions in the database
        sql = """SELECT COUNT(DISTINCT root_tag_id) AS count FROM DIMENSIONS"""

        def extract_count(count):
            return count

        return execute_sql_fetch_single(extract_count, sql)

    def add_dimension(self, tag):
        # Input: A tag that is not already a root
        # Side effect: A new dimension has been created in the database
        # Output: The root node of the valid dimension tree
        if not isinstance(tag, Tag) or not tag.id:
            raise ObjectCubeException(
                'Must give DimensionNode with valid root_tag_id')

        # Create the root node
        root_node = DimensionNode(root_tag_id=tag.id,
                                  node_tag_id=tag.id,
                                  node_tag_value=tag.value,
                                  left_border=0,
                                  right_border=0,
                                  child_nodes=[]);

        # Construct a valid tree, first in memory, then on disk
        self._calculate_borders(root_node)
        self._write_nodes(root_node)

        # Return a valid tree from disk to make sure
        return self.retrieve_dimension_by_root(root_node)

    def add_node(self, root_node, parent_tag, child_tag):
        # Input: A valid root node, a parent tag (in the tree) and a child tag
        # Side effect: The child_tag has been inserted as a sub-node of the node containing parent_tag
        # Output: The root node of the resulting valid dimension tree
        if not isinstance(root_node, DimensionNode) or \
                not isinstance(parent_tag, Tag) or \
                not isinstance(child_tag, Tag):
            raise ObjectCubeDatabaseException('Input not of correct types')

        # Create the child
        child_node = DimensionNode(root_tag_id=root_node.root_tag_id,
                                   node_tag_id=child_tag.id,
                                   node_tag_value=child_tag.value,
                                   child_nodes=[])

        # Get the tree, find the parent, insert the child
        root_node = self._read_nodes(root_node)
        parent_node = self._find_node(root_node, parent_tag.id)
        parent_node.child_nodes.append(child_node)

        # repair the tree, first in memory, then on disk (delete and write)
        self._calculate_borders(root_node)
        self._delete(root_node)
        self._write_nodes(root_node)

        # return the tree root node
        return self.retrieve_dimension_by_root(root_node)

    def retrieve_dimension_roots(self):
        return self._read_roots()

    def retrieve_dimension_roots_by_tag(self, tag):
        if not isinstance(tag, Tag):
            raise ObjectCubeDatabaseException('Invalid tag')

        return self._read_roots(tag)

    def retrieve_dimension_by_root(self, root_node):
        # Input: A valid root node
        # Output: The root node of the corresponding valid dimension tree
        if not isinstance(root_node, DimensionNode) or \
                not root_node.root_tag_id or \
                not root_node.node_tag_id or \
                not root_node.root_tag_id == root_node.node_tag_id:
            raise ObjectCubeDatabaseException('Invalid root node')

        return self._read_nodes(root_node)

    def delete(self, subtree_root_node):
        # Input: The root node of a valid sub-tree structure
        # Side effect: The sub-tree has been deleted from the database
        # Output: None
        if not isinstance(subtree_root_node, DimensionNode) or not subtree_root_node.root_tag_id or \
                not subtree_root_node.node_tag_id or not subtree_root_node.left_border or not subtree_root_node.right_border:
            raise ObjectCubeException(
                'Must give DimensionNode with valid root_tag_id, node_tag_id, left_border and right_border')
        self._delete(subtree_root_node)

    def print_tree(self, root_node, indent=''):
        # Input: A root node of a valid tree structure, an initial indentation
        # Side effect: A representation of the tree has been printed to the screen
        # Output: None
        print indent, 'root=', root_node.root_tag_id, 'node=', root_node.node_tag_id, 'L=', root_node.left_border, ' R=', root_node.right_border
        for node in root_node.child_nodes:
            self.print_tree(node, indent + '  ')
        return None

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