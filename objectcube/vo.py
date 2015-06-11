import json


class SerializableMixin(object):
    def __init__(self, **kwargs):
        self.data = {}
        for field in self.fields:
            if field not in kwargs:
                self.data[field] = None

            self.data[field] = kwargs.get(field)

    def __getattr__(self, key):
        if key not in self.data:
            raise Exception('Class {} does not have a field with name {}'
                            .format(self.__class__, key))
        return self.data.get(key)

    def __setattr__(self, key, value):
        super(SerializableMixin, self).__setattr__(key, value)
        self.data[key] = value

    def __eq__(self, other):
        for f in self.fields:
            if getattr(self, f) != getattr(other, f):
                return False
        return True


class Tag(SerializableMixin):
    fields = ['id', 'value', 'description', 'mutable', 'type',
              'concept_id', 'plugin_id']

    def __init__(self, **kwargs):
        super(Tag, self).__init__(**kwargs)

    def __str__(self):
        return self.value

    def __repr__(self):
        return str(self.data.get('id'))


class Tagging(SerializableMixin):
    fields = ['id', 'tag_id', 'object_id', 'meta', 'plugin_id',
              'plugin_set_id']

    def __init__(self, **kwargs):
        super(Tagging, self).__init__(**kwargs)

    def __str__(self):
        return self.id

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__,
                                 repr(self.data))

class Concept(SerializableMixin):
    fields = ['id', 'title', 'description']

    def __init__(self, **kwargs):
        super(Concept, self).__init__(**kwargs)

    def __str__(self):
        return self.id

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__,
                                 repr(self.data))

    def to_dict(self):
        return {
            'title': self.title, 'description':
            self.description, 'id': self.id
        }


class Plugin(SerializableMixin):
    fields = ['id', 'name', 'module']

    def __init__(self, **kwargs):
        super(Plugin, self).__init__(**kwargs)


class Object(SerializableMixin):
    fields = ['id', 'name', 'digest']

    def __init__(self, **kwargs):
        super(Object, self).__init__(**kwargs)

    def __eq__(self, other):
        for k in self.fields:
            if getattr(self, k) != getattr(other, k):
                return False
        return True


class DimensionNode(SerializableMixin):
    fields = [
        'root_tag_id',
        'node_tag_id',
        'node_tag_value',
        'left_border',
        'right_border',
        'child_nodes'
    ]

    def __init__(self, **kwargs):
        super(DimensionNode, self).__init__(**kwargs)


class Tree(object):
    def __init__(self, tag_id, name=None):
        self.name = name
        self.tag_id = tag_id
        self.children = []

    def serialize(self):
        """
        :return:
        """
        data = {'name': self.name, 'tag_id': self.tag_id, 'children': []}

        for c in self.children:
            data.get('children').append(self._serialize_recursion(c))

        return data

    def _serialize_recursion(self, root):
        children = []

        for c in root.children:
            children.append(self._serialize_recursion(c))

        return {'tag_id': root.tag_id, 'children': children}

    def add_child(self, tree):
        """
        :param tree:
        :return:
        """
        self.children.append(tree)
        return tree

    def remove_child(self, tag_id):
        """
        :param tree:
        :return:
        """
        for c in self.children:
            if c.tag_id == tag_id:
                self._remove_subtrees(c)
                self.children.remove(c)
                return True
        return False

    def _remove_subtrees(self, root):
        for c in root.children:
            root._remove_subtrees(c)
            root.children.remove(c)
            del c

    def get_child(self, tag_id):
        for c in self.children:
            if c.tag_id == tag_id:
                return c

    @staticmethod
    def deserialize_tree(data):
        root = Tree(tag_id=data.get('tag_id'), name=data.get('name'))
        for c in data.get('children'):
            root.add_child(Tree._deserialize_recursive(c))
        return root

    @staticmethod
    def _deserialize_recursive(node):
        children = []
        for c in node.get('children'):
            children.append(Tree._deserialize_recursive(c))

        t = Tree(tag_id=node.get('tag_id'))
        t.children = children
        return t
