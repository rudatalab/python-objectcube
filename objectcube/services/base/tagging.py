from service import Service
from objectcube.vo import Plugin


class BaseTaggingService(Service):

    def count(self):
        raise NotImplementedError()

    def add(self, tag, object, meta, plugin=None, plugin_set_id=None):
        raise NotImplementedError()

    def delete_by_set_id(self, plugin_set_id):
        raise NotImplementedError()

    def resolve(self, tag, object, meta, plugin, plugin_set_id):
        raise NotImplementedError()

    def delete(self, tagging):
        raise NotImplementedError()

    def retrieve_by_id(self, id):
        raise NotImplementedError()

    def retrieve_by_tag_id(self, tag_id, offset=0, limit=10):
        raise NotImplementedError()

    def retrieve_by_object_id(self, object_id, offset=0, limit=10):
        raise NotImplementedError()

    def retrieve_by_set_id(self, plugin_set_id, offset=0, limit=10):
        raise NotImplementedError()

    def update(self, tagging):
        raise NotImplementedError()
