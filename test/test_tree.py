from unittest import TestCase
from objectcube.vo import Tree


class TestTreeConstructions(TestCase):
    def test_single_node_tre(self):
        t = Tree(1, name='foobar')
        data = t.serialize()
        self.assertTrue(data.get('name') == 'foobar')
        self.assertTrue(len(data.get('children')) == 0)
        self.assertTrue(data.get('tag_id') == 1)

    def test_root_with_one_children(self):
        t = Tree(1, name='foobar')
        t.children.append(Tree(2))

        data = t.serialize()

        self.assertTrue(data.get('name') == 'foobar')
        self.assertTrue(len(data.get('children')) == 1)
        self.assertTrue(data.get('tag_id') == 1)

        data = data.get('children')[0]

        self.assertFalse(data.get('name'))
        self.assertTrue(len(data.get('children')) == 0)
        self.assertTrue(data.get('tag_id') == 2)

    def test_root_with_two_children(self):
        t = Tree(1, name='foobar')
        t.children.append(Tree(2))
        t.children.append(Tree(3))

        data = t.serialize()

    def test_root_with_extra_level(self):
        root = Tree(1, name='root')
        tree = root.add_child(Tree(1))
        tree.add_child(Tree(2))
        tree.add_child(Tree(3))
        root.add_child(Tree(4))
        data = root.serialize()