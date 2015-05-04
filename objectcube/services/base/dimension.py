from service import Service


class BaseDimensionService(Service):

    def add_dimension(self, tag):
        '''Returns root node'''
        raise NotImplementedError()

    def add_node(self, parent_node, tag):
        ''' tag is a child tag '''
        raise NotImplementedError()

    def delete(self, subtree_root_node):
        raise NotImplementedError()

    def retrieve_dimension(self, tag):
        raise NotImplementedError()

