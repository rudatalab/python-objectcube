from service import Service


class BaseTaggingService(Service):

    def count(self):
        raise NotImplementedError()

    def add(self, tagging):
        raise NotImplementedError()

    def update(self, tagging):
        raise NotImplementedError()

    def resolve(self, tagging):
        raise NotImplementedError()

    def delete_by_set_id(self, plugin_set_id):
        raise NotImplementedError()

    def delete(self, tagging):
        raise NotImplementedError()

    def retrieve_by_id(self, id_):
        raise NotImplementedError()

    def retrieve_by_tag_id(self, tag_id, offset=0L, limit=10L):
        raise NotImplementedError()

    def retrieve_by_object_id(self, object_id, offset=0L, limit=10L):
        raise NotImplementedError()

    def retrieve_by_set_id(self, plugin_set_id, offset=0L, limit=10L):
        raise NotImplementedError()
