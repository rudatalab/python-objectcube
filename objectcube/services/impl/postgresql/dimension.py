from utils import execute_sql_fetch_single, execute_sql_fetch_multiple
from objectcube.services.base import BaseDimensionService
from objectcube.exceptions import ObjectCubeException
from objectcube.data_objects import DimensionNode
from types import LongType
from logging import getLogger


class DimensionService(BaseDimensionService):
    def __init__(self):
        super(DimensionService, self).__init__()
        self.logger = getLogger('postgreSQL: DimensionService')

    def _calculate_borders(self, root_node, counter=None):
        # Input: Root node of a valid tree structure
        # Output: Nothing
        # Side effect: The left_border and right_border values
        #              are correct in the input tree.
        if counter is None:
            counter = [1L]

        root_node.left_border = counter[0]
        counter[0] += 1

        if root_node.child_nodes:
            for node in root_node.child_nodes:
                if not isinstance(node, DimensionNode):
                    raise ObjectCubeException('Invalid child in tree')
                self._calculate_borders(node, counter)

        root_node.right_border = counter[0]
        counter[0] += 1

    def _construct_tree(self, nodes, counter=None):
        # Input: Array of nodes representing a valid tree structure,
        #        without any linking
        # Output: The root node of a valid tree structure
        if counter is None:
            counter = [0L]

        parent = DimensionNode(
            root_tag_id=nodes[counter[0]].root_tag_id,
            node_tag_id=nodes[counter[0]].node_tag_id,
            node_tag_value=nodes[counter[0]].node_tag_value,
            left_border=nodes[counter[0]].left_border,
            right_border=nodes[counter[0]].right_border,
            child_nodes=[]
        )
        counter[0] += 1

        while True:
            if counter[0] >= len(nodes) \
                    or nodes[counter[0]].right_border > parent.right_border:
                return parent
            parent.child_nodes.append(
                self._construct_tree(nodes, counter))

    def _insert_node(self, node):
        # Input: A single tree node
        # Side effect: The tree node has been written to the database
        # Output: The Node written
        sql = 'INSERT ' \
              'INTO DIMENSIONS ( ' \
              '  ROOT_TAG_ID, NODE_TAG_ID, LEFT_BORDER, RIGHT_BORDER' \
              ') ' \
              'VALUES( %s, %s, %s, %s) ' \
              'RETURNING *'
        params = (node.root_tag_id, node.node_tag_id,
                  node.left_border, node.right_border)
        return execute_sql_fetch_single(DimensionNode, sql, params)

    def _write_nodes(self, root_node, root_tag_id=None):
        # Input: The root node of a valid tree structure
        # Side effect: The tree has been written to the database
        # Output: The root node
        if not root_tag_id:
            root_tag_id = root_node.root_tag_id

        # Ensure the correct root node, then write
        root_node.root_tag_id = root_tag_id
        self._insert_node(root_node)

        # Write all children, and return
        for child in root_node.child_nodes:
            self._write_nodes(child, root_tag_id)
        return root_node

    def _read_tree(self, root_node):
        # Input: A valid root node
        # Output: The root node of a valid tree structure
        sql = ('SELECT D.root_tag_id, D.node_tag_id, T.value, '
               '       D.left_border, D.right_border '
               'FROM Dimensions D '
               '  JOIN Tags T ON D.node_tag_id = T.id '
               'WHERE D.root_tag_id = %s '
               'ORDER BY D.left_border ASC')
        params = (root_node.root_tag_id,)
        nodes = execute_sql_fetch_multiple(DimensionNode, sql, params)
        if len(nodes) == 0:
            return None
        return self._construct_tree(nodes)

    def _read_roots(self, tag_id=None):
        # Input: An optional tag
        # Output: An array of all the root nodes
        #         (of dimensions that contain the tag)
        if tag_id is not None:
            sql = 'SELECT D1.root_tag_id, D1.node_tag_id, T1.value ' \
                  'FROM Dimensions D1 ' \
                  '  JOIN Dimensions D2 ON D1.root_tag_id = D2.root_tag_id ' \
                  '  JOIN Tags T1 ON D1.node_tag_id = T1.id ' \
                  'WHERE D1.root_tag_id = D1.node_tag_id ' \
                  '  AND D2.node_tag_id = %s ' \
                  'ORDER BY D1.left_border ASC'
            params = (tag_id,)
        else:
            sql = ('SELECT D.root_tag_id, D.node_tag_id, T.value '
                   'FROM Dimensions D '
                   '  JOIN Tags T ON D.node_tag_id = T.id '
                   'WHERE D.root_tag_id = D.node_tag_id '
                   'ORDER BY D.left_border ASC')
            params = None
        return execute_sql_fetch_multiple(DimensionNode, sql, params)

    def _delete_all(self, root_node):
        sql = 'DELETE ' \
              'FROM DIMENSIONS ' \
              'WHERE root_tag_id = %s ' \
              'RETURNING *'
        params = (root_node.root_tag_id, )
        execute_sql_fetch_single(DimensionNode, sql, params)
        return None

    def count(self):
        self.logger.debug('count()')
        sql = 'SELECT ' \
              'COUNT(DISTINCT root_tag_id) AS count ' \
              'FROM DIMENSIONS'
        return execute_sql_fetch_single(lambda count: count, sql)

    def add(self, root):
        self.logger.debug('add(): %s', repr(root))

        if not isinstance(root, DimensionNode):
            raise ObjectCubeException('Function requires valid node')

        # Construct a valid tree, first in memory, then on disk
        self._calculate_borders(root)
        self._write_nodes(root)

        # Return a valid tree from disk to make sure
        return self.retrieve_dimension(root)

    def update_or_create(self, root):
        self.logger.debug('replace_or_create_dimension(): %s', repr(root))

        if not isinstance(root, DimensionNode):
            raise ObjectCubeException('Function requires valid root')

        # Make the tree correct, this checks the structure
        # If the structure is not ok, then an exception is raised
        # which can safely be passed to the caller
        self._calculate_borders(root)

        # Retrieve the old tree, if it exists, for safekeeping, then delete it
        old_tree = self.retrieve_dimension(root)
        if old_tree:
            self._delete_all(old_tree)

        # Then we write the new tree
        # If it fails then we reinstall the old tree and raise exception
        # Otherwise return the new tree and be happy :)
        try:
            self._write_nodes(root)
        except:
            self._delete_all(root)
            self._write_nodes(old_tree)
            raise ObjectCubeException('Could not replace with illegal tree')

        # Return the result
        return self.retrieve_dimension(root)

    def delete(self, root):
        self.logger.debug('delete(): %s', repr(root))

        if not isinstance(root, DimensionNode):
            raise ObjectCubeException('Function requires valid root node')

        if not self._read_tree(root):
            raise ObjectCubeException('No dimension found to delete')

        self._delete_all(root)
        return None

    def retrieve_roots(self):
        self.logger.debug('retrieve_dimension_roots()')
        return self._read_roots()

    def retrieve_roots_by_tag_id(self, tag_id):
        self.logger.debug('retrieve_dimension_roots_by_tag(): %s',
                          repr(tag_id))

        if not isinstance(tag_id, LongType):
            raise ObjectCubeException('Function requires valid Tag id')

        return self._read_roots(tag_id)

    def retrieve_dimension(self, root):
        self.logger.debug('retrieve_dimension(): %s',
                          repr(root))

        if not isinstance(root, DimensionNode):
            raise ObjectCubeException('Function requires valid root node')

        return self._read_tree(root)
