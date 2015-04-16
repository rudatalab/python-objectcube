from service import Service


class BaseObjectService(Service):
    def add(self, object):
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

    def retrieve_by_id(self, object_id):
        """
        Retrieves a given object by id
        :param object_id: Number representing the value of the object.
        :return: Object if found, None otherwise.
        """
        raise NotImplementedError()

    def retrieve(self, offset=0, limit=10):
        raise NotImplementedError()


    def retrieve_by_tag(self, tag, offset=0, limit=10):
        raise NotImplementedError()