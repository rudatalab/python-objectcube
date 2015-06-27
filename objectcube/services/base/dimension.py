from service import Service


class BaseDimensionService(Service):

    def count(self):
        raise NotImplementedError()

    def add(self, root_node):
        raise NotImplementedError()

    def update_or_create(self, root_node):
        raise NotImplementedError()

    def delete(self, root_node):
        raise NotImplementedError()

    def retrieve_roots(self):
        raise NotImplementedError()

    def retrieve_roots_by_tag_id(self, tag_id):
        raise NotImplementedError()

    def retrieve_dimension(self, root_node):
        raise NotImplementedError()
