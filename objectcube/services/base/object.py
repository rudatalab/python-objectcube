from service import Service

class BaseObjectService(Service):
    def count(self):
        """
        Counts the number of objects in data store.
        Note that this value may not be accurate
        :return: Number of Object in database as number
        """
        raise NotImplementedError()

    def add(self, object_):
        """
        Add object to data store.
        :param: object_: Instance of Object to insert (without id)
        :return: the Object stored in the database
        """
        raise NotImplementedError()

    def update(self, object_):
        """
        Updates the given object
        :param: object_: instance of Object to update
        :return: updated object
        """
        raise NotImplementedError()

    def delete_by_id(self, id_):
        """
        Deletes a given object from the database
        :param: id_: identifier of Object to delete
        :return: None, raises exception if none found
        """
        raise NotImplementedError()

    def delete(self, object_):
        """
        Deletes a given object from the database
        :param: object_: instance of Object to delete
        :return: None, raises exception if none found
        """
        raise NotImplementedError()

    def retrieve_by_id(self, id_):
        """
        Retrieves a given object by id
        :param: id_: the identifier of the Object
        :return: Object if found, None otherwise
        """
        raise NotImplementedError()

    def retrieve(self, offset=0L, limit=10L):
        """
        Retrieves all objects in database
        :param: offset: the first object to return
        :param: limit: the number of objects to return
        :return: [Object], empty set if none found
        """
        raise NotImplementedError()

    def retrieve_by_regex(self, name, offset=0L, limit=10L):
        """
        Retrieves a given object by regular expression on name
        :param: name: regular expression to match on name
        :param: offset: the first object to return
        :param: limit: the number of objects to return
        :return: [Object], empty set if none found
        """
        raise NotImplementedError()

    def retrieve_by_tag(self, tag, offset=0L, limit=10L):
        """
        Retrieves all objects tagged with a particular tag
        :param: tag: tag to match
        :param: offset: the first object to return
        :param: limit: the number of objects to return
        :return: [Object], empty set if none found
        """
        raise NotImplementedError()
