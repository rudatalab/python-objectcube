from service import Service
from objectcube.vo import Plugin


class BaseTaggingService(Service):

    def add(self, object, tag, meta, plugin=Plugin(), plugin_set_id=None):
        raise NotImplementedError()

    def delete_by_set_id(self, plugin_set_id):
        raise NotImplementedError()

    def resolve(self, object, tag, meta, plugin=Plugin(), plugin_set_id=None):
        raise NotImplementedError()

    def delete(self, tagging):
        raise NotImplementedError()

    def update(self, tagging):
        raise NotImplementedError()
