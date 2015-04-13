from service import Service

class BaseDimensionService(Service):

    def add_dimension(self, tree):
        """
        Insert Dimension into database as a tree.
        :param tree: The tree object that should be added.
        :return: Returns nothing.
        """
        raise NotImplementedError()

    def get_dimensions(self):
        """
        Retrieve all Dimension objects from database.
        :return: List of dimensions
        """
        raise NotImplementedError()

    def get_by_id(self, _id):
        """
        Fetches dimension by id.
        :param _id: ID for the Dimension to retrieve.
        :return: Dimension object if found, None otherwise
        """
        raise NotImplementedError()

    def get_by_name(self, name):
        """
        Fetches Dimension by name.
        :param name: Name of the Dimension to retrieve.
        :return: Dimension object matching the name.
        """
        raise NotImplementedError()

    def update_dimension(self, name, new_dimension):
        """
        Update a dimension.
        :param name: Name of the dimension to modify.
        :return: Returns nothing.
        """
        raise NotImplementedError()
