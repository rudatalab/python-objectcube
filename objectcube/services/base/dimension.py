from service import Service


class BaseDimensionService(Service):

    def count(self):
        raise NotImplementedError()

    def add_dimension(self, tag):
        raise NotImplementedError()

    def retrieve_dimension_roots(self):
        raise NotImplementedError()

    def retrieve_dimension_roots_by_tag(self, tag):
        raise NotImplementedError()

    def delete(self, subtree_root_node):
        raise NotImplementedError()

    def add_node(self, root_node, parent_tag, child_tag):
        raise NotImplementedError()

    def retrieve_dimension_by_root(self, root_node):
        raise NotImplementedError()

    def replace_or_create_dimension(self, root_node):
        raise NotImplementedError()
