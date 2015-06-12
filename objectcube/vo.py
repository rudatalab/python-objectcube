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

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__,
                                 repr(self.to_dict()))

    def __eq__(self, other):
        for f in self.fields:
            if getattr(self, f) != getattr(other, f):
                return False
        return True

    def to_dict(self):
        out = {}
        for field in self.fields:
            out[field] = self.data[field]
        return out

    def serialize(self):
        pass

class Tag(SerializableMixin):
    fields = ['id',
              'value',
              'description',
              'mutable',
              'type',
              'concept_id',
              'plugin_id']

    def __init__(self, **kwargs):
        super(Tag, self).__init__(**kwargs)

class Tagging(SerializableMixin):
    fields = ['id',
              'tag_id',
              'object_id',
              'meta',
              'plugin_id',
              'plugin_set_id']

    def __init__(self, **kwargs):
        super(Tagging, self).__init__(**kwargs)

class Concept(SerializableMixin):
    fields = ['id',
              'title',
              'description']

    def __init__(self, **kwargs):
        super(Concept, self).__init__(**kwargs)

class Plugin(SerializableMixin):
    fields = ['id',
              'name',
              'module']

    def __init__(self, **kwargs):
        super(Plugin, self).__init__(**kwargs)

class Object(SerializableMixin):
    fields = ['id',
              'name',
              'digest']

    def __init__(self, **kwargs):
        super(Object, self).__init__(**kwargs)

class DimensionNode(SerializableMixin):
    fields = ['root_tag_id',
              'node_tag_id',
              'node_tag_value',
              'left_border',
              'right_border',
              'child_nodes']

    def __init__(self, **kwargs):
        super(DimensionNode, self).__init__(**kwargs)
