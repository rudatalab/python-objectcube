from base import TestDatabaseAwareTest
from objectcube.factory import get_service
from objectcube.exceptions import ObjectCubeException
from objectcube.data_objects import Tag, DimensionNode, Concept


class TestDimensionService(TestDatabaseAwareTest):
    def __init__(self, *args, **kwargs):
        super(TestDimensionService, self).__init__(*args, **kwargs)
        self.dimension_service = get_service('DimensionService')
        self.tag_service = get_service('TagService')
        self.concept_service = get_service('ConceptService')

    def _create_test_concept(self, title=u'', description=u''):
        """
        Helper function for creating concepts in tests.
        :param: values for concept properties
        :return: A concept that has not been added to data store.
        """
        return self.concept_service.add(Concept(title=title,
                                                description=description))

    def _create_test_concepts(self):
        """
        Helper function for creating concepts in tests.
        :param: values for tag properties
        :return: A tag that has not been added to data store.
        """
        self._create_test_concept(title=u'People',
                                  description=u'All people in the world')
        self._create_test_concept(title=u'Object',
                                  description=u'All objects in the world')

    def _create_test_tag(self, value=u'', description=u'DESC', concept_id=1L):
        """
        Helper function for creating db tags in tests.
        :param: values for tag properties
        :return: A tag that has already been added to data store.
        """
        return self.tag_service.add(Tag(value=value,
                                        description=description,
                                        mutable=False,
                                        type=0L,
                                        concept_id=concept_id))

    def _create_test_tags(self, values=None, concept_id=None):
        """
        Helper function for creating db tags in tests.
        :param values: Values for the tags to be created.
        :return: Array of tags which have already been added to data store.
        """
        tags = []
        for value in values:
            tags.append(self._create_test_tag(value=value,
                                              concept_id=concept_id))

        self.assertEquals(len(values), len(tags))
        return tags

    def _add_child(self, parent_node, child_node):
        parent_node.child_nodes.append(child_node)

    def _print_nodes(self, root_node, indent=''):
        print indent, repr(root_node)
        for i in range(0, len(root_node.child_nodes)):
            self._print_nodes(root_node.child_nodes[i], indent+'  ')

    def _count_nodes(self, root_node):
        count = 0
        for i in range(0, len(root_node.child_nodes)):
            count += self._count_nodes(root_node.child_nodes[i])
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
            if not self._test_dimension_equal(root1.child_nodes[i],
                                              root2.child_nodes[i]):
                return False
        return True

    def _setup_large_dimension(self):
        tags = self._create_test_tags([
            u'People', u'Classmates', u'RU', u'Jack',
            u'Jill', u'MH', u'Bob', u'Alice', u'John'],
            concept_id=1L)

        root_node = DimensionNode(root_tag_id=tags[0].id,
                                  node_tag_id=tags[0].id,
                                  child_nodes=[])
        level_2 = DimensionNode(root_tag_id=tags[0].id,
                                node_tag_id=tags[1].id,
                                child_nodes=[])
        self._add_child(root_node, level_2)
        level_3 = DimensionNode(root_tag_id=tags[0].id,
                                node_tag_id=tags[2].id,
                                child_nodes=[])
        self._add_child(level_2, level_3)
        level_4 = DimensionNode(root_tag_id=tags[0].id,
                                node_tag_id=tags[3].id,
                                child_nodes=[])
        self._add_child(level_3, level_4)
        level_4 = DimensionNode(root_tag_id=tags[0].id,
                                node_tag_id=tags[4].id,
                                child_nodes=[])
        self._add_child(level_3, level_4)
        level_3 = DimensionNode(root_tag_id=tags[0].id,
                                node_tag_id=tags[5].id,
                                child_nodes=[])
        self._add_child(level_2, level_3)
        level_4 = DimensionNode(root_tag_id=tags[0].id,
                                node_tag_id=tags[6].id,
                                child_nodes=[])
        self._add_child(level_3, level_4)
        level_4 = DimensionNode(root_tag_id=tags[0].id,
                                node_tag_id=tags[7].id,
                                child_nodes=[])
        self._add_child(level_3, level_4)
        level_2 = DimensionNode(root_tag_id=tags[0].id,
                                node_tag_id=tags[8].id,
                                child_nodes=[])
        self._add_child(root_node, level_2)

        self.assertEquals(self._count_nodes(root_node), len(tags),
                          msg='Not enough nodes in hierarchy')
        return self.dimension_service.add(root_node)

    def _setup_small_dimension(self):
        tags = self._create_test_tags([u'Bill', u'RU'], concept_id=2L)

        root_node = DimensionNode(root_tag_id=tags[1].id,
                                  node_tag_id=tags[1].id,
                                  child_nodes=[])
        level_2 = DimensionNode(root_tag_id=tags[1].id,
                                node_tag_id=tags[0].id,
                                child_nodes=[])
        self._add_child(root_node, level_2)

        self.assertEquals(self._count_nodes(root_node), len(tags),
                          msg='Not enough nodes in hierarchy')
        return self.dimension_service.add(root_node)

    def test_dimension_equal_correct(self):
        self._create_test_concepts()
        large_root = self._setup_large_dimension()
        db_root = self.dimension_service.retrieve_dimension(large_root)
        self.assertTrue(self._test_dimension_equal(db_root, large_root))

    # ==== count()

    def test_dimension_initial_count_zero(self):
        self.assertEquals(self.dimension_service.count(), 0)

    def test_dimension_count_correct(self):
        self._create_test_concepts()
        self.assertEquals(self.dimension_service.count(), 0)
        self._setup_small_dimension()
        self.assertEquals(self.dimension_service.count(), 1)
        self._setup_large_dimension()
        self.assertEquals(self.dimension_service.count(), 2)

    # ==== add()

    def test_dimension_add_dimension_few_tags(self):
        self._create_test_concepts()
        count_nodes = self._count_nodes(self._setup_small_dimension())

        roots = self.dimension_service.retrieve_roots()
        self.assertEquals(len(roots), 1)

        tags = self.tag_service.retrieve_by_value(u'Bill')
        self.assertEquals(len(tags), 1)

        roots = self.dimension_service.retrieve_roots_by_tag_id(tags[0].id)
        self.assertEquals(len(roots), 1)

        root_node = self.dimension_service.retrieve_dimension(roots[0])
        self.assertEquals(self._count_nodes(root_node), count_nodes)

    def test_dimension_add_dimension_many_tags(self):
        self._create_test_concepts()
        count_nodes = self._count_nodes(self._setup_large_dimension())

        roots = self.dimension_service.retrieve_roots()
        self.assertEquals(len(roots), 1)

        tags = self.tag_service.retrieve_by_value(u'Jill')
        self.assertEquals(len(tags), 1)

        roots = self.dimension_service.retrieve_roots_by_tag_id(tags[0].id)
        self.assertEquals(len(roots), 1)

        root_node = self.dimension_service.retrieve_dimension(roots[0])
        self.assertEquals(self._count_nodes(root_node), count_nodes)

    def test_dimension_add_two_dimensions(self):
        self._create_test_concepts()
        small_nodes = self._count_nodes(self._setup_small_dimension())
        large_nodes = self._count_nodes(self._setup_large_dimension())

        roots = self.dimension_service.retrieve_roots()
        self.assertEquals(len(roots), 2)

        tags = self.tag_service.retrieve_by_value(u'Jill')
        self.assertEquals(len(tags), 1)

        roots = self.dimension_service.retrieve_roots_by_tag_id(tags[0].id)
        self.assertEquals(len(roots), 1)

        root_node = self.dimension_service.retrieve_dimension(roots[0])
        self.assertEquals(self._count_nodes(root_node), large_nodes)

        roots = self.dimension_service.retrieve_roots()
        self.assertEquals(len(roots), 2)

        tags = self.tag_service.retrieve_by_value(u'Bill')
        self.assertEquals(len(tags), 1)

        roots = self.dimension_service.retrieve_roots_by_tag_id(tags[0].id)
        self.assertEquals(len(roots), 1)

        root_node = self.dimension_service.retrieve_dimension(roots[0])
        self.assertEquals(self._count_nodes(root_node), small_nodes)

    def test_dimension_add_raises_with_illegal_input(self):
        self._create_test_concepts()
        self._setup_small_dimension()
        self._setup_large_dimension()

        with self.assertRaises(ObjectCubeException):
            self.dimension_service.add('1')

        with self.assertRaises(ObjectCubeException):
            self.dimension_service.add(0)

        with self.assertRaises(ObjectCubeException):
            self.dimension_service.add(None)
        self.assertEquals(self.dimension_service.count(), 2)

    def test_dimension_add_raises_with_unknown_roots(self):
        self._create_test_concepts()
        self._setup_small_dimension()
        self._setup_large_dimension()

        with self.assertRaises(ObjectCubeException):
            root_node = DimensionNode(root_tag_id=30L,
                                      node_tag_id=30L)
            self.dimension_service.add(root_node)
        with self.assertRaises(ObjectCubeException):
            root_node = DimensionNode(root_tag_id=30L,
                                      node_tag_id=1L)
            self.dimension_service.add(root_node)
        with self.assertRaises(ObjectCubeException):
            root_node = DimensionNode(root_tag_id=1L,
                                      node_tag_id=30L)
            self.dimension_service.add(root_node)
        self.assertEquals(self.dimension_service.count(), 2)

    def test_dimension_add_raises_with_duplicate_root(self):
        self._create_test_concepts()
        self._setup_small_dimension()
        self._setup_large_dimension()

        root_node = DimensionNode(root_tag_id=1L,
                                  node_tag_id=1L,
                                  child_nodes=[])

        # First insert OK, second not
        self.dimension_service.add(root_node)
        with self.assertRaises(ObjectCubeException):
            self.dimension_service.add(root_node)

        self.assertEquals(self.dimension_service.count(), 3)

    def test_dimension_add_raises_illegal_tree(self):
        self._create_test_concepts()
        self._setup_small_dimension()
        self._setup_large_dimension()

        root_node = DimensionNode(root_tag_id=1L,
                                  node_tag_id=1L,
                                  child_nodes=[1, 3, 4])
        with self.assertRaises(ObjectCubeException):
            self.dimension_service.add(root_node)

        self.assertEquals(self.dimension_service.count(), 2)

    # ==== delete()

    def test_dimension_delete_works(self):
        self._create_test_concepts()
        self.assertEquals(self.dimension_service.count(), 0)
        small_root = self._setup_small_dimension()
        self.assertEquals(self.dimension_service.count(), 1)
        large_root = self._setup_large_dimension()
        self.assertEquals(self.dimension_service.count(), 2)
        out = self.dimension_service.delete(small_root)
        self.assertIsNone(out)
        self.assertEquals(self.dimension_service.count(), 1)
        out = self.dimension_service.delete(large_root)
        self.assertIsNone(out)
        self.assertEquals(self.dimension_service.count(), 0)

    def test_dimension_delete_raises_illegal_tree(self):
        self._create_test_concepts()
        self._setup_small_dimension()
        self._setup_large_dimension()

        root_node = DimensionNode(root_tag_id=1L,
                                  node_tag_id=1L,
                                  child_nodes=[1, 3, 4])
        with self.assertRaises(ObjectCubeException):
            self.dimension_service.delete(root_node)

        self.assertEquals(self.dimension_service.count(), 2)

    def test_dimension_delete_raises_non_existing_tree(self):
        self._create_test_concepts()
        self._setup_small_dimension()
        self._setup_large_dimension()

        root_node = DimensionNode(root_tag_id=1L,
                                  node_tag_id=1L,
                                  child_nodes=[])
        with self.assertRaises(ObjectCubeException):
            self.dimension_service.delete(root_node)

        self.assertEquals(self.dimension_service.count(), 2)

    def test_dimension_delete_raises_illegal_root(self):
        self._create_test_concepts()
        self._setup_small_dimension()
        self._setup_large_dimension()

        with self.assertRaises(ObjectCubeException):
            self.dimension_service.delete(1)
        with self.assertRaises(ObjectCubeException):
            self.dimension_service.delete(True)
        with self.assertRaises(ObjectCubeException):
            self.dimension_service.delete(False)
        with self.assertRaises(ObjectCubeException):
            self.dimension_service.delete(0)
        with self.assertRaises(ObjectCubeException):
            self.dimension_service.delete('ID')
        with self.assertRaises(ObjectCubeException):
            self.dimension_service.delete(3.1415297)
        with self.assertRaises(ObjectCubeException):
            self.dimension_service.delete([])

        self.assertEquals(self.dimension_service.count(), 2)

    # ==== retrieve_roots_by_tag_id()

    def test_dimension_retrieve_roots_by_tag_id_raises_on_illegal_tags(self):
        self._create_test_concepts()
        self._setup_small_dimension()
        self._setup_large_dimension()

        with self.assertRaises(ObjectCubeException):
            self.dimension_service.retrieve_roots_by_tag_id('1')
        with self.assertRaises(ObjectCubeException):
            self.dimension_service.retrieve_roots_by_tag_id(0)
        with self.assertRaises(ObjectCubeException):
            self.dimension_service.retrieve_roots_by_tag_id(None)
        with self.assertRaises(ObjectCubeException):
            self.dimension_service.retrieve_roots_by_tag_id(True)
        with self.assertRaises(ObjectCubeException):
            self.dimension_service.retrieve_roots_by_tag_id(False)
        with self.assertRaises(ObjectCubeException):
            self.dimension_service.retrieve_roots_by_tag_id(1)

    def test_dimension_retrieve_roots_by_tag_id_returns_no_roots_tags(self):
        self._create_test_concepts()
        self._setup_small_dimension()
        self._setup_large_dimension()

        self.assertEquals(
            len(self.dimension_service.retrieve_roots_by_tag_id(42L)), 0)

    # ==== retrieve_dimension()

    def test_dimension_retrieve_dimension_raises_on_illegal_roots(self):
        self._create_test_concepts()
        self._setup_small_dimension()
        self._setup_large_dimension()

        with self.assertRaises(ObjectCubeException):
            self.dimension_service.retrieve_dimension('1')

        with self.assertRaises(ObjectCubeException):
            self.dimension_service.retrieve_dimension(0)

        with self.assertRaises(ObjectCubeException):
            self.dimension_service.retrieve_dimension(None)

        with self.assertRaises(ObjectCubeException):
            self.dimension_service.retrieve_dimension(True)

        with self.assertRaises(ObjectCubeException):
            self.dimension_service.retrieve_dimension(False)

    def test_dimension_retrieve_dimension_returns_none_non_existing_root(self):
        self._create_test_concepts()
        self._setup_small_dimension()
        self._setup_large_dimension()

        fake_root = DimensionNode(root_tag_id=42L,
                                  node_tag_id=42L,
                                  child_nodes=[])
        fake_dim = self.dimension_service.retrieve_dimension(fake_root)
        self.assertIsNone(fake_dim)

    # ==== update_or_create()

    def test_dimension_replace_or_create_replaces(self):
        self._create_test_concepts()
        self._setup_small_dimension()
        self._setup_large_dimension()

        roots = self.dimension_service.retrieve_roots()
        self.assertEquals(len(roots), 2)

        # Get a copy of the small dimension, then delete it from the database
        small_dim = self.dimension_service.retrieve_dimension(roots[0])
        small_cnt = self._count_nodes(small_dim)
        self.dimension_service.delete(roots[0])
        self.assertEquals(len(self.dimension_service.retrieve_roots()), 1)

        # Change the root of the copy to be the same as the large dimension
        small_dim.root_tag_id = roots[1].root_tag_id
        small_dim.node_tag_id = roots[1].node_tag_id

        # Replace the large dimension by the modified copy
        new_dim = self.dimension_service.update_or_create(small_dim)
        self.assertEquals(self._count_nodes(new_dim), small_cnt)
        self.assertEquals(len(self.dimension_service.retrieve_roots()), 1)
        self.assertTrue(self._test_dimension_equal(small_dim, new_dim))

    def test_dimension_replace_or_create_creates(self):
        self._create_test_concepts()
        self._setup_small_dimension()
        self._setup_large_dimension()

        roots = self.dimension_service.retrieve_roots()
        self.assertEquals(len(roots), 2)

        # Get a copy of the small dimension, then delete it from the database
        small_dim = self.dimension_service.retrieve_dimension(roots[0])
        small_cnt = self._count_nodes(small_dim)
        self.dimension_service.delete(roots[0])
        self.assertEquals(len(self.dimension_service.retrieve_roots()), 1)

        # Reinsert small dimension
        new_dim = self.dimension_service.update_or_create(small_dim)
        self.assertEquals(self._count_nodes(new_dim), small_cnt)
        self.assertEquals(len(self.dimension_service.retrieve_roots()), 2)
        self.assertTrue(self._test_dimension_equal(small_dim, new_dim))

    def test_dimension_replace_or_create_illegal_tree_leaves_tree_ok(self):
        self._create_test_concepts()
        self._setup_large_dimension()
        self._setup_small_dimension()

        # Try structurally unsound dimension
        root_node = DimensionNode(root_tag_id=1L,
                                  node_tag_id=1L,
                                  child_nodes=[1, 3, 4])
        with self.assertRaises(ObjectCubeException):
            self.dimension_service.update_or_create(root_node)

        # Make note of large dimension
        roots = self.dimension_service.retrieve_roots()
        before_node = self.dimension_service.retrieve_dimension(roots[0])

        # Make an illegal reference to a tag, and try to create or replace it
        root_node = self.dimension_service.retrieve_dimension(roots[0])
        root_node.child_nodes[0].node_tag_id += 200L
        with self.assertRaises(ObjectCubeException):
            self.dimension_service.update_or_create(root_node)

        # Ensure nothing changed
        self.assertEquals(self.dimension_service.count(), 2)
        after_node = self.dimension_service.retrieve_dimension(roots[0])
        self.assertTrue(self._test_dimension_equal(before_node, after_node))

    def test_dimension_replace_or_create_raises_with_illegal_roots(self):
        self._create_test_concepts()
        self._setup_small_dimension()
        self._setup_large_dimension()

        with self.assertRaises(ObjectCubeException):
            self.dimension_service.update_or_create('1')
        with self.assertRaises(ObjectCubeException):
            self.dimension_service.update_or_create(0)
        with self.assertRaises(ObjectCubeException):
            self.dimension_service.update_or_create(None)
        with self.assertRaises(ObjectCubeException):
            self.dimension_service.update_or_create(False)
        with self.assertRaises(ObjectCubeException):
            self.dimension_service.update_or_create(True)
        with self.assertRaises(ObjectCubeException):
            self.dimension_service.update_or_create(1)
