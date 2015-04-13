from service import Service


class BaseObjectService(Service):
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