from base import TestDatabaseAwareTest
from objectcube.factory import get_service
from objectcube.exceptions import ObjectCubeException
from objectcube.vo import Tag, DimensionNode
from random import shuffle

class TestDimensionService(TestDatabaseAwareTest):
    def __init__(self, *args, **kwargs):
        super(TestDimensionService, self).__init__(*args, **kwargs)
        self.dimension_service = get_service('DimensionService')
        self.tag_service = get_service('TagService')

    def _create_test_tag(self, _value=''):
        print 'creating TAG'
        return Tag(
            id = None,
            value = _value,
            description = '',
            mutable = False,
            type = 0,
            concept_id = 0,
            plugin_id = 0)

    def _add_test_tags(self, values=None):
        """
        Helper function for creating db tags in tests.
        :param values: Values for the tags to be created.
        :return: Array of tags which have not been added to data store.
        """
        tags = []
        #shuffle(values)
        for value in values:
            tag = self._create_test_tag(value)
            print tag.value
            tags.append(self.tag_service.add(tag))
        self.assertEquals(len(values), len(tags))
        return tags

    def _count_nodes(self, root_node):
        return root_node.right_border/2

    def _test_dimension_equal(self, root1, root2):
        if root1.root_tag_id != root2.root_tag_id:
            return False
        if root1.node_tag_id != root2.node_tag_id:
            return False
        if root1.node_tag_value != root2.node_tag_value:
            return False
        if not root1.child_nodes and root2.child_nodes:
            return False
        if root1.child_nodes and not root2.child_nodes:
            return False
        if not root1.child_nodes and not root2.child_nodes:
            return True
        if len(root1.child_nodes) != len(root2.child_nodes):
            return False
        for i in range(0, len(root1.child_nodes)):
            if not self._test_dimension_equal(root1.child_nodes[i], root2.child_nodes[i]):
                return False
        return True

    def test_dimensions_initial_count_zero(self):
        self.assertEquals(self.dimension_service.count(), 0,
                          msg='No dimensions should be in the data store')

    def test_dimensions_count_correct(self):
        #import pdb; pdb.set_trace()
        tag = self.tag_service.add(self._create_test_tag(value='Test'))
        db_node = self.dimension_service.add_dimension(tag)

        self.assertEquals(self._count_nodes(db_node), 1,
                          msg='Dimension should have one node')

    def test_dimensions_equal_correct(self):
        tag = self.tag_service.add(self._create_test_tag(value='Test'))
        db_node = self.dimension_service.add_dimension(tag)
        #import pdb; pdb.set_trace()
        root1 = self.dimension_service.retrieve_dimension_by_root(db_node)
        root2 = self.dimension_service.retrieve_dimension_by_root(db_node)
        self.assertTrue(self._test_dimension_equal(root1, root2),
                          msg='Dimension equality is not correct')

    def test_dimensions_add_dimension(self):
        tag = self.tag_service.add(self._create_test_tag(value='Test'))
        db_node = self.dimension_service.add_dimension(tag)
        self.assertEquals(self.dimension_service.count(), 1,
                          msg='Dimension has not been added')

    def test_dimensions_delete_dimension(self):
        tag = self.tag_service.add(self._create_test_tag(value='Test'))
        db_node = self.dimension_service.add_dimension(tag)
        self.dimension_service.delete(db_node)
        self.assertEquals(self.dimension_service.count(), 0,
                          msg='Dimension has not been deleted')

    def test_dimension_many_tags(self):
        import pdb; pdb.set_trace()
        tags = self._add_test_tags(['People', 'Classmates', 'RU', 'Jack', 'Jill', 'MH', 'Bob', 'Alice', 'John'])
        root_node = self.dimension_service.add_dimension(tags[0])
        self.dimension_service.add_node(root_node, tags[0], tags[1])
        self.assertEquals(self._count_nodes(root_node), 2,
                          msg='Not enough nodes in hierarchy')

