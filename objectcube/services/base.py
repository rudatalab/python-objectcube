class BaseTagService(object):
    def get_tags(self, offset=0, limit=10):
        """
        Fetch tags from data store.
        :param offset: The offset value for the result.
        :param limit: The limit value for the result.
        :return: List of Tag objects.
        """
        raise NotImplementedError()

    def add_tag(self, tag):
        """
        Adds new tag to data store.
        :param tag: Tag object filled with data. Note that the id field must
        be set to None when creating new tag.
        :return: None
        """
        raise NotImplementedError()

    def count(self):
        """
        Returns the count of all tags in data store. Note that this value might
        not be accurate. This value should be thought of as estimate
        of the tag count.
        :return: Integer
        """
        raise NotImplementedError()

    def get_by_id(self, _id):
        """
        Fetches tag by id.
        :param _id: Id for a given Tag.
        :return: Tag object if found, None otherwise
        """
        raise NotImplementedError()

    def get_by_value(self, value):
        """
        Fetches tags by value.
        :param value: Value to fetch.
        :return: List of tag objects, or empty list if none are found.
        """
        raise NotImplementedError()


class BasePluginService(object):
    def count(self):
        raise NotImplementedError()

    def get_plugins(self):
        raise NotImplementedError()

    def get_plugin_by_name(self):
        raise NotImplementedError()

    def get_plugin_by_id(self):
        raise NotImplementedError()

    def add_plugin(self, plugin):
        raise NotImplementedError()

    def process(self, _object, _data):
        raise NotImplementedError()


class BaseObjectService(object):
    def __init__(self):
        self.blob_service = None

    def add(self, stream, name):
        raise NotImplementedError()

    def count(self):
        raise NotImplementedError()

    def add_tags_to_objects(self, objects, tags):
        """
        Add tags to objects. All tags in the tags parameter
        will be applied to all objects in the objects parameter.
        """
        raise NotImplementedError()

    def get_objects_by_tags(self, tags):
        """
        Fetch objects that have been applied with tags in tags
        """
        raise NotImplementedError()

    def get_by_id(self, id):
        raise NotImplementedError()

    def get_objects(self, offset=0, limit=10):
        raise NotImplementedError()


class BaseDimensionService(object):
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


class BaseBlobService(object):
    pass
