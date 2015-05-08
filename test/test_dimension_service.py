from base import TestDatabaseAwareTest
from objectcube.factory import get_service
from objectcube.exceptions import ObjectCubeException
from objectcube.vo import Tag, DimensionNode, Concept

class TestDimensionService(TestDatabaseAwareTest):
    def __init__(self, *args, **kwargs):
        super(TestDimensionService, self).__init__(*args, **kwargs)
        self.dimension_service = get_service('DimensionService')
        self.tag_service = get_service('TagService')
        self.concept_service = get_service('ConceptService')

    def _create_test_concept(self, _title='', _description=''):
        """
        Helper function for creating concepts in tests.
        :param: values for concept properties
        :return: A concept that has not been added to data store.
        """
        return self.concept_service.add(Concept(title=_title,
                                                description=_description))

    def _create_test_concepts(self):
        """
        Helper function for creating concepts in tests.
        :param: values for tag properties
        :return: A tag that has not been added to data store.
        """
        self._create_test_concept(_title='People', _description='All people in the world')
        self._create_test_concept(_title='Object', _description='All objects in the world')

    def _create_test_tag(self, _value='', _description='', _concept_id=1):
        """
        Helper function for creating db tags in tests.
        :param: values for tag properties
        :return: A tag that has already been added to data store.
        """
        return self.tag_service.add(Tag(id=None,
                                        value=_value,
                                        description=_description,
                                        mutable=False,
                                        type=0,
                                        concept_id=_concept_id,
                                        plugin_id=None))

    def _create_test_tags(self, values=None, _concept_id=None):
        """
        Helper function for creating db tags in tests.
        :param values: Values for the tags to be created.
        :return: Array of tags which have already been added to data store.
        """
        tags = []
        for value in values:
            tags.append(self._create_test_tag(value, _concept_id))

        self.assertEquals(len(values), len(tags))
        return tags

    def _count_nodes(self, root_node):
        return root_node.right_border/2

    def _count_nodes_recursive(self, root_node):
        count = 0
        for i in range(0, len(root_node.child_nodes)):
            count += self._count_nodes_recursive(root_node.child_nodes[i])
        return count+1

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

    def _setup_large_dimension(self):
        tags = self._create_test_tags(['People', 'Classmates', 'RU', 'Jack', 'Jill', 'MH', 'Bob', 'Alice', 'John'],
                                      _concept_id=1)

        root_node = self.dimension_service.add_dimension(tags[0])
        root_node = self.dimension_service.add_node(root_node, tags[0], tags[1])
        root_node = self.dimension_service.add_node(root_node, tags[1], tags[2])
        root_node = self.dimension_service.add_node(root_node, tags[2], tags[3])
        root_node = self.dimension_service.add_node(root_node, tags[2], tags[4])
        root_node = self.dimension_service.add_node(root_node, tags[1], tags[5])
        root_node = self.dimension_service.add_node(root_node, tags[0], tags[8])
        root_node = self.dimension_service.add_node(root_node, tags[5], tags[6])
        root_node = self.dimension_service.add_node(root_node, tags[5], tags[7])
        self.assertEquals(self._count_nodes(root_node), len(tags),
                          msg='Not enough nodes in hierarchy')
        self.assertEquals(self._count_nodes(root_node), self._count_nodes_recursive(root_node),
                          msg='Node count methods disagree')

    def _setup_small_dimension(self):
        tags = self._create_test_tags(['Bill', 'RU'],
                                      _concept_id=2)

        root_node = self.dimension_service.add_dimension(tags[1])
        root_node = self.dimension_service.add_node(root_node, tags[1], tags[0])
        self.assertEquals(self._count_nodes(root_node), len(tags),
                          msg='Not enough nodes in hierarchy')
        self.assertEquals(self._count_nodes(root_node), self._count_nodes_recursive(root_node),
                          msg='Node count methods disagree')

    def test_dimension_many_tags(self):
        self._create_test_concepts()
        self._setup_large_dimension()
        roots = self.dimension_service.retrieve_dimension_roots()
        self.assertEquals(len(roots), 1,
            msg='Wrong number of roots')
        #import pdb; pdb.set_trace()
        tags = self.tag_service.retrieve_by_value('Jack')
        self.assertEquals(len(tags), 1,
            msg='Tags')
        roots = self.dimension_service.retrieve_dimension_roots_by_tag(tags[0])
        self.assertEquals(len(roots), 1, msg='Wrong number of roots attached to Jack')

    def test_dimension_few_tags(self):
        self._create_test_concepts()
        self._setup_small_dimension()
        self._setup_large_dimension()

        roots = self.dimension_service.retrieve_dimension_roots()
        self.assertEquals(len(roots), 2,
            msg='Wrong number of roots')
        tags = self.tag_service.retrieve_by_value('Jack')
        self.assertEquals(len(tags), 1,
            msg='Tags')

        # Delete the large dimension
        roots = self.dimension_service.retrieve_dimension_roots_by_tag(tags[0])
        self.dimension_service.delete(roots[0])

        roots = self.dimension_service.retrieve_dimension_roots()
        self.assertEquals(len(roots), 1,
            msg='Wrong number of roots after delete')
        tags = self.tag_service.retrieve_by_value('Jack')
        self.assertEquals(len(tags), 1,
            msg='Tags')
        roots = self.dimension_service.retrieve_dimension_roots_by_tag(tags[0])
        self.assertEquals(len(roots), 0, msg='Wrong number of roots attached to Jack after delete')

    def test_two_dimensions(self):
        self._create_test_concepts()
        self._setup_small_dimension()
        self._setup_large_dimension()

        roots = self.dimension_service.retrieve_dimension_roots()
        self.assertEquals(len(roots), 2,
            msg='Wrong number of roots')
        tags = self.tag_service.retrieve_by_value('Jack')
        self.assertEquals(len(tags), 1,
            msg='Tags')
        roots = self.dimension_service.retrieve_dimension_roots_by_tag(tags[0])
        self.assertEquals(len(roots), 1,
            msg='Wrong number of roots')

    def test_dimensions_initial_count_zero(self):
        self.assertEquals(self.dimension_service.count(), 0,
                          msg='No dimensions should be in the data store')

    def test_dimensions_count_correct(self):
        self._create_test_concepts()
        tag = self._create_test_tag(_value='Test')
        db_node = self.dimension_service.add_dimension(tag)

        self.assertEquals(self._count_nodes(db_node), 1,
                          msg='Dimension should have one node')

    def test_dimensions_equal_correct(self):
        self._create_test_concepts()
        tag = self._create_test_tag(_value='Test')
        db_node = self.dimension_service.add_dimension(tag)
        root1 = self.dimension_service.retrieve_dimension_by_root(db_node)
        root2 = self.dimension_service.retrieve_dimension_by_root(db_node)
        self.assertTrue(self._test_dimension_equal(root1, root2),
                          msg='Dimension equality is not correct')

    def test_dimensions_add_dimension(self):
        self._create_test_concepts()
        tag = self._create_test_tag('Test')
        db_node = self.dimension_service.add_dimension(tag)
        self.assertEquals(self.dimension_service.count(), 1,
                          msg='Dimension has not been added')

    def test_dimensions_delete_dimension(self):
        self._create_test_concepts()
        tag = self._create_test_tag('Test')
        db_node = self.dimension_service.add_dimension(tag)
        self.dimension_service.delete(db_node)
        self.assertEquals(self.dimension_service.count(), 0,
                          msg='Dimension has not been deleted')

