from exceptions import ObjectCubeException
from types import LongType, UnicodeType, BooleanType, NoneType, ListType


class ObjectCubeClass(object):
    def __init__(self, **kwargs):
        self.data = {}
        for key, type_ in self.fields.items():
            # Type checking is only done on the specified fields
            # of each class, allowing to set other fields to anything
            # If a string is given, it must be non-empty
            if not isinstance(kwargs.get(key), type_) \
                    or kwargs.get(key) == u'':
                raise ObjectCubeException(
                    'Init invalid type: Class {}; Field {}; Value {}; '
                    'Desired Type {}; Given Type {}'
                    .format(self.__class__, key, kwargs.get(key),
                            type_, type(kwargs.get(key))))
            self.data[key] = kwargs.get(key)

    def __getattr__(self, key):
        if key not in self.data:
            raise ObjectCubeException(
                'Get invalid field: Class {}; Field {}'
                .format(self.__class__, key))
        return self.data.get(key)

    def __setattr__(self, key, value):
        super(ObjectCubeClass, self).__setattr__(key, value)
        # Type checking is only done on the specified fields
        # of each class to allow the statement self.data = {} in __init__
        if key in self.fields \
                and (not isinstance(value, self.fields[key]) or value == u''):
            raise ObjectCubeException(
                'Set invalid type: Class {}; Field {}; Value {};'
                'Desired Type {}; Given Type {}'
                .format(self.__class__, key, value,
                        self.fields[key], type(value)))
        self.data[key] = value

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__,
                                 repr(self.__dict__()))

    def __eq__(self, other):
        for f in self.fields:
            if getattr(self, f) != getattr(other, f):
                return False
        return True

    def __dict__(self):
        out = {}
        for field in self.fields:
            out[field] = self.data[field]
        return out

    def serialize(self):
        pass


class Plugin(ObjectCubeClass):
    fields = {'id': (LongType, NoneType),
              'name': UnicodeType,
              'module': UnicodeType}

    def __init__(self, **kwargs):
        super(Plugin, self).__init__(**kwargs)


class Concept(ObjectCubeClass):
    fields = {'id': (LongType, NoneType),
              'title': UnicodeType,
              'description': UnicodeType}

    def __init__(self, **kwargs):
        super(Concept, self).__init__(**kwargs)


class Object(ObjectCubeClass):
    fields = {'id': (LongType, NoneType),
              'name': UnicodeType,
              'digest': UnicodeType}

    def __init__(self, **kwargs):
        super(Object, self).__init__(**kwargs)


class Tag(ObjectCubeClass):
    fields = {'id': (LongType, NoneType),
              'value': UnicodeType,
              'description': UnicodeType,
              'mutable': BooleanType,
              'type': LongType,
              'concept_id': (LongType, NoneType),
              'plugin_id': (LongType, NoneType)}

    def __init__(self, **kwargs):
        super(Tag, self).__init__(**kwargs)


class Tagging(ObjectCubeClass):
    fields = {'id': (LongType, NoneType),
              'tag_id': LongType,
              'object_id': LongType,
              'meta': (UnicodeType, NoneType),
              'plugin_id': (LongType, NoneType),
              'plugin_set_id': (LongType, NoneType)}

    def __init__(self, **kwargs):
        super(Tagging, self).__init__(**kwargs)


class DimensionNode(ObjectCubeClass):
    fields = {'root_tag_id': LongType,
              'node_tag_id': LongType,
              'node_tag_value': UnicodeType,
              'left_border': LongType,
              'right_border': LongType,
              'child_nodes': ListType}

    def __init__(self, **kwargs):
        super(DimensionNode, self).__init__(**kwargs)
