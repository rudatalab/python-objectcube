from service import Service


class BasePluginService(Service):

    def count(self):
        raise NotImplementedError()

    def add(self, plugin):
        raise NotImplementedError()

    def retrieve_by_id(self, id):
        raise NotImplementedError()

    def retrieve_by_name(self, name):
        raise NotImplementedError()

    def retrieve(self, offset=0, limit=10):
        raise NotImplementedError()

    def retrieve_by_regex(self, regex, offset=0, limit=10):
        raise NotImplementedError()
