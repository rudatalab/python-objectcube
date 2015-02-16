from unittest import TestCase
from objectcube.vo import Tree


class TestTreeSerialize(TestCase):
    def test_single_node_tre(self):
        root = Tree(1, name='foobar')
        actual = root.serialize()
        expected = {'name': 'foobar', 'children': [], 'tag_id': 1}
        self.assertDictEqual(actual, expected)

    def test_root_with_one_children(self):
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
    def test_single_node_tre(self):
        serialized_tree = {
            'name': 'foobar',
            'children': [],
            'tag_id': 1
        }
        tree = Tree.deserialize_tree(serialized_tree)

        self.assertDictEqual(serialized_tree,
                             tree.serialize())

    def test_root_with_one_children(self):
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
