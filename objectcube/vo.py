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
                            .format(self.__class__.__str__(), key))
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
    fields = ['id', 'value', 'description', 'mutable', 'type', 'plugin_id']

    def __init__(self, **kwargs):
        super(Tag, self).__init__(**kwargs)

    def __str__(self):
        return self.value

    def __repr__(self):
        return str(self.data.get('id'))


class Plugin(SerializableMixin):
    fields = ['id', 'name', 'module']

    def __init__(self, **kwargs):
        super(Plugin, self).__init__(**kwargs)


class Object(SerializableMixin):
    fields = ['id', 'name', 'resource_uri']

    def __init__(self, **kwargs):
        super(Object, self).__init__(**kwargs)


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

        return {'tag_id': root.tag_id, 'children': children }

    def add_child(self, tree):
        """
        :param tree:
        :return:
        """
        self.children.append(tree)
        return tree

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