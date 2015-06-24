from service import Service


class BaseTagService(Service):

    def count(self):
        raise NotImplementedError()

    def add(self, tag):
        raise NotImplementedError()

    def retrieve_or_create(self, tag):
        raise NotImplementedError()

    def update(self, tag):
        raise NotImplementedError()

    def delete_by_id(self, id_):
        raise NotImplementedError()

    def delete(self, tag):
        raise NotImplementedError()

    def retrieve_by_id(self, id_):
        raise NotImplementedError()

    def retrieve(self, offset=0L, limit=10L):
        raise NotImplementedError()

    def retrieve_by_value(self, value, offset=0L, limit=10L):
        raise NotImplementedError()

    def retrieve_by_plugin(self, plugin, offset=0L, limit=10L):
        raise NotImplementedError()

    def retrieve_by_concept(self, concept, offset=0L, limit=10L):
        raise NotImplementedError()
