from unittest import TestCase
from objectcube.vo import Tree


class TestTreeAddChild(TestCase):
    def test_tree_only_root_node(self):
        root = Tree(1, name='foobar')
        new_child = Tree(2)
        self.assertTrue(len(root.children) == 0)
        root.add_child(new_child)
        self.assertTrue(len(root.children) == 1)

    def test_tree_another_level_below_root(self):
        root = Tree(1, name='foobar')
        child = root.add_child(Tree(2))
        self.assertTrue(len(root.children) == 1)
        child.add_child(Tree(3))
        self.assertTrue(len(root.children) == 1)
        self.assertTrue(len(root.children[0].children) == 1)
        self.assertEquals(child.children[0], root.children[0].children[0])


class TestTreeSerialize(TestCase):
    def test_single_node_tree(self):
        root = Tree(1, name='foobar')
        actual = root.serialize()
        expected = {'name': 'foobar', 'children': [], 'tag_id': 1}
        self.assertDictEqual(actual, expected)

    def test_root_with_one_child(self):
        root = Tree(tag_id=1, name='foobar')
        root.children.append(Tree(tag_id=2))
        actual = root.serialize()
        expected = {
            'tag_id': 1,
            'name': 'foobar',
            'children': [
                {
                    'tag_id': 2,
                    'children': []
                }
            ]}
        self.assertDictEqual(actual, expected)

    def test_root_with_two_children(self):
        t = Tree(1, name='foobar')
        t.children.append(Tree(2))
        t.children.append(Tree(3))

        actual = t.serialize()
        expected = {
            'name': 'foobar',
            'tag_id': 1,
            'children': [
                {
                    'tag_id': 2,
                    'children': []
                },
                {
                    'tag_id': 3,
                    'children': []
                }
            ]
        }
        self.assertDictEqual(actual, expected)

    def test_root_with_extra_level(self):
        root = Tree(1, name='root')
        tree = root.add_child(Tree(1))
        tree.add_child(Tree(2))
        tree.add_child(Tree(3))
        root.add_child(Tree(4))
        actual = root.serialize()
        expected = {
            'name': 'root',
            'tag_id': 1,
            'children': [
                {
                    'tag_id': 1,
                    'children': [
                        {
                            'tag_id': 2,
                            'children': []
                        },
                        {
                            'tag_id': 3,
                            'children': []
                        }
                    ]
                },
                {
                    'tag_id': 4,
                    'children': []
                }

            ]
        }
        self.assertDictEqual(actual, expected)


class TestTreeDeserialize(TestCase):
    def test_single_node_tree(self):
        serialized_tree = {
            'name': 'foobar',
            'children': [],
            'tag_id': 1
        }
        tree = Tree.deserialize_tree(serialized_tree)

        self.assertDictEqual(serialized_tree,
                             tree.serialize())

    def test_root_with_one_child(self):
        serialized_tree = {
            'tag_id': 1,
            'name': 'foobar',
            'children': [
                {
                    'tag_id': 2,
                    'children': []
                }
            ]}

        tree = Tree.deserialize_tree(serialized_tree)
        self.assertDictEqual(serialized_tree, tree.serialize())

    def test_another_level_below_root(self):
        serialized_tree = {
            'tag_id': 1,
            'name': 'foobar',
            'children': [
                {
                    'tag_id': 2,
                    'children': [
                        {
                            'tag_id': 3,
                            'children': []
                        },
                        {
                            'tag_id': 4,
                            'children': []
                        }
                    ]
                }
            ]
        }
        tree = Tree.deserialize_tree(serialized_tree)
        self.assertDictEqual(serialized_tree, tree.serialize())


class TestTreeRemoveChild(TestCase):
    def test_remove_child_that_has_no_children(self):
        root = Tree(1, name='foobar')
        root.add_child(Tree(2))
        self.assertTrue(len(root.children) == 1)
        removed = root.remove_child(2)
        self.assertTrue(removed)
        self.assertTrue(len(root.children) == 0)

    def test_remove_child_tag_id_does_not_exist(self):
        root = Tree(1, name='foobar')
        root.add_child(Tree(2))
        self.assertTrue(len(root.children) == 1)
        removed = root.remove_child(3)
        self.assertFalse(removed)
        self.assertTrue(len(root.children) == 1)

    def test_remove_child_that_has_children(self):
        root = Tree(1, name='foobar')
        new_child = root.add_child(Tree(2))
        new_child.add_child(Tree(3))
        self.assertTrue(len(root.children) == 1)
        self.assertTrue(len(new_child.children) == 1)
        removed = root.remove_child(2)
        self.assertTrue(removed)
        self.assertTrue(len(root.children) == 0)


class TestTreeGetChild(TestCase):
    def test_get_child_that_does_not_exist(self):
        root = Tree(1, name='foobar')
        root.add_child(Tree(2))
        child = root.get_child(4)
        self.assertNotIsInstance(child, Tree)
        self.assertIsNone(child)

    def test_get_child_that_exists(self):
        root = Tree(1, name='foobar')
        new_child = root.add_child(Tree(2))
        child = root.get_child(2)
        self.assertEquals(new_child, child)
