from service import Service


class BasePluginService(Service):

    def count(self):
        raise NotImplementedError()

    def add(self, plugin):
        raise NotImplementedError()

    def retrieve_by_id(self, id_):
        raise NotImplementedError()

    def retrieve_by_name(self, name):
        raise NotImplementedError()

    def retrieve(self, offset=0L, limit=10L):
        raise NotImplementedError()

    def retrieve_by_regex(self, name, offset=0L, limit=10L):
        raise NotImplementedError()
