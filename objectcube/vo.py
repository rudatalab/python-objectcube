class SerializableMixin(object):
    def __init__(self, **kwargs):
        self.data = {}
        for field in self.fields:
            if field not in kwargs:
                raise Exception('expected argument of name {}'.format(field))

            self.data[field] = kwargs.get(field)

    def serialize(self):
        raise Exception('Not implemented')

    def deserialize(self):
        raise Exception('Not implemented')

    def validate_value(self):
        raise Exception('Not implemented')

    def __getattr__(self, key):
        if key not in self.data:
            raise Exception('Class {} does not have a field with name {}'
                            .format(self.__class__.__str__(), key))
        return self.data.get(key)


class ConceptType(SerializableMixin):
    DATE = 'DATE'
    TIME = 'TIME'
    DATETIME = 'DATETIME'
    ALPHANUMERICAL = 'ALPHANUMERICAL'
    NUMERICAL = 'NUMERICAL'
    REGEX = 'REGEX'

    fields = ['id', 'name', 'regex_pattern', 'concept_base_type']
    allowed_types = [DATE, DATETIME, TIME, ALPHANUMERICAL, NUMERICAL, REGEX]
    default_type = ALPHANUMERICAL

    def __init__(self, **kwargs):
        super(ConceptType, self).__init__(**kwargs)

    def __repr__(self):
        return self.name


class Concept(SerializableMixin):
    fields = ['id', 'name', 'description', 'concept_type_id']

    def __init__(self, **kwargs):
        super(Concept, self).__init__(**kwargs)

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        for field in self.fields:
            if getattr(self, field) != getattr(other, field):
                return False
        return True
