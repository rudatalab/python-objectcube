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
        :return: Returns the newly created tag object. It is the same tag
        object passed in by parameter, with updated id value.
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
        """
        Add object to data store.
        :param stream: Stream to data.
        :param name: Name of the object. This can be a name that describes
        the object being added.
        :return: Object filled with the added object details.
        """
        raise NotImplementedError()

    def count(self):
        """
        Counts the number of objects in data store. Note that this value
        might not be accurate
        :return: Number of objects as number
        """
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

    def get_by_id(self, object_id):
        """
        Fetch a given object by id
        :param object_id: Number representing the value of the object.
        :return: Object if found, None otherwise.
        """
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
    """
    Base class for blob services. The purpose of this service is to mange
    uploads and uri handling for blob objects in the ObjectCube model.

    The implementation decides where the blobs are stored and what metadata
    is kept with each blob. Implementations could be storing files on
    file system, AWS-S3, Swift, etc.

    Blobs are identified by MD5 checksums. This allows us to reuse objects
    without duplicating them.
    """
    def has_blob(self, digest_id):
        """
        Checks if a given blob digest id has been added.
        :param digest_id: Digest sum for a content of a given file.
        :return: True if blob has been added, false otherwise.
        """
        raise NotImplementedError()

    def add_blob(self, fs, blob_meta, digest=None):
        """
        Adds a give blob.
        :param fs: Stream to file, or memory.
        :param blob_meta: Dictionary of meta-data that should be stored
        with the blob (size, content-type, etc)
        :param digest: Digest of the sum. This field is optional. If not
        provided then md5 will be calculated on the fs.
        :return: None
        """
        raise NotImplementedError()

    def get_uri(self, digest):
        """
        Returns URI to the blob. This can vary by implementations. For
        filesystem implementation this could we the path to the file or for
        Swift, this can be a temporary URL to the blob.
        :param digest: Digest of blob that has been added.
        :return: URI string if blob has been added, None otherwise.
        """
        raise NotImplementedError()

    def flush(self):
        """
        Flushes all blobs that have been added.
        :return: None
        """
        raise NotImplementedError()

    def get_blob_meta(self, digest):
        """
        Fetch blob meta data, if added, for a given blob.
        :param digest: Digest for a blob that has been added.
        :return: Dictionary with meta-data if found, None otherwise.
        """
        raise NotImplementedError()
