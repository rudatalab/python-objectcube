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


class Tag(SerializableMixin):
    fields = ['id', 'value', 'description', 'mutable', 'type', 'plugin_id']

    def __init__(self, **kwargs):
        super(Tag, self).__init__(**kwargs)

    def __str__(self):
        return self.value

    def __repr__(self):
        return str(self.data.get('id'))

    def __eq__(self, other):
        for f in self.fields:
            if getattr(self, f) != getattr(other, f):
                return False
        return True
