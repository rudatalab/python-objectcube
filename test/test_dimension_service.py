from base import TestDatabaseAwareTest
from objectcube.vo import Tree
from objectcube.factory import get_service_class
from objectcube.exceptions import ObjectCubeException


class TestDimensionService(TestDatabaseAwareTest):
    def __init__(self, *args, **kwargs):
        super(TestDimensionService, self).__init__(*args, **kwargs)
        self.dimension_service = get_service_class('DimensionService')

    def _create_test_tree(self, name='foobar'):
        root = Tree(1, name=name)
        first_child = root.add_child(Tree(2))
        root.add_child(Tree(3))
        first_child.add_child(Tree(4))
        return root

    def test_add_dimension_should_return_id(self):
        dim = self._create_test_tree('foo')
        self.dimension_service.add_dimension(dim)
        self.assertTrue(dim.id, msg='Adding a dimension should set an ID')
        self.assertEquals(dim.id, 1, msg='First addition should have ID 1')

    def test_get_dimensions_returns_list(self):
        self.assertTrue(isinstance(
            self.dimension_service.get_dimensions(), list),
            msg='The return value from get_tags should be of type list')

    def test_get_dimensions_with_empty_database(self):
        dims = self.dimension_service.get_dimensions()
        self.assertTrue(len(dims) == 0, msg='The return value from '
                        'get_dimensions should be an empty list')

    def test_get_dimension_returns_list_of_trees(self):
        foo = self._create_test_tree('foo')
        bar = self._create_test_tree('bar')
        self.dimension_service.add_dimension(foo)
        self.dimension_service.add_dimension(bar)
        trees = self.dimension_service.get_dimensions()
        self.assertTrue(len(trees) == 2, msg='Adding two dimensions should '
                        'save two records in the database.')

    def test_get_by_nonexisting_id_returns_none(self):
        result = self.dimension_service.get_by_id(1)
        self.assertIsNone(result, msg='Nonexisting IDs should return None')

    def test_get_by_id_should_return_correct_object(self):
        dim = self._create_test_tree('foobar')
        self.dimension_service.add_dimension(dim)
        dim_get = self.dimension_service.get_by_id(1)
        self.assertEquals(dim.serialize(), dim_get.serialize(),
                          msg='Fetching an object by its ID should return '
                          'the correct object')

    def test_get_by_bogus_name_should_throw_error(self):
        with self.assertRaises(ObjectCubeException):
            self.dimension_service.get_by_name(1)

        with self.assertRaises(ObjectCubeException):
            self.dimension_service.get_by_name('')

        with self.assertRaises(ObjectCubeException):
            self.dimension_service.get_by_name([])

    def test_get_by_name_should_return_correct_object(self):
        dim = self._create_test_tree('foobar')
        self.dimension_service.add_dimension(dim)
        dim_get = self.dimension_service.get_by_name('foobar')
        self.assertEquals(dim.serialize(), dim_get.serialize(),
                          msg='Fetching an object by its name should return '
                          'the correct object')

    def test_update_dimension_bogus_input_throws(self):
        tree = self._create_test_tree('foo')
        with self.assertRaises(ObjectCubeException):
            self.dimension_service.update_dimension('', tree)

        with self.assertRaises(ObjectCubeException):
            self.dimension_service.update_dimension('', 1)

        with self.assertRaises(ObjectCubeException):
            self.dimension_service.update_dimension('foo', 1)

    def test_update_dimension_name_should_update_object(self):
        dim = self._create_test_tree('foobar')
        old_name = dim.name
        old_children = dim.serialize().get('children')
        self.dimension_service.add_dimension(dim)
        dim.name = 'foo'
        self.dimension_service.update_dimension(old_name, dim)
        new_dim = self.dimension_service.get_by_id(dim.id)
        new_children = new_dim.serialize().get('children')
        self.assertTrue(new_dim.name == 'foo')
        self.assertEquals(old_children, new_children)
        self.assertTrue(new_dim.tag_id == dim.tag_id)

    def test_update_dimension_children_should_update_object(self):
        dim = self._create_test_tree('foobar')
        self.dimension_service.add_dimension(dim)
        self.assertTrue(len(dim.children) == 2)
        dim.add_child(Tree(2))
        self.dimension_service.update_dimension(dim.name, dim)
        new_dim = self.dimension_service.get_by_name(dim.name)
        self.assertEquals(new_dim.serialize(), dim.serialize())
        self.assertTrue(new_dim.name == 'foobar')
        self.assertTrue(len(new_dim.children) == 3)
