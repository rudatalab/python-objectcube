from service import Service

class BaseObjectService(Service):
    def count(self):
        """
        Counts the number of objects in data store.
        Note that this value may not be accurate
        :return: Number of objectcube.vo.Object in database as number
        """
        raise NotImplementedError()

    def add(self, obj):
        """
        Add object to data store.
        :param object: Instance of objectcube.vo.Object to insert (without id)
        :return: the objectcube.vo.Object stored in the database
        """
        raise NotImplementedError()

    def update(self, obj):
        """
        Updates the given object
        :param obj: instance of objectcube.vo.Object to update
        :return: updated object
        """
        raise NotImplementedError()

    def delete_by_id(self, id):
        """
        Deletes a given object from the database
        :param id: identifier of objectcube.vo.Object to delete
        :return: None, raises exception if none found
        """
        raise NotImplementedError()

    def delete(self, obj):
        """
        Deletes a given object from the database
        :param obj: instance of objectcube.vo.Object to delete
        :return: None, raises exception if none found
        """
        raise NotImplementedError()

    def retrieve_by_id(self, id):
        """
        Retrieves a given object by id
        :param id: the identifier of the objectcube.vo.Object
        :return: objectcube.vo.Object if found, None otherwise
        """
        raise NotImplementedError()

    def retrieve(self, offset=0, limit=10):
        """
        Retrieves all objects in database
        :param offset: the first object to return
        :param limit: the number of objects to return
        :return: [objectcube.vo.Object], empty set if none found
        """
        raise NotImplementedError()

    def retrieve_by_regex(self, name, offset=0, limit=10):
        """
        Retrieves a given object by regular expression on name
        :param name: regular expression to match on name
        :param offset: the first object to return
        :param limit: the number of objects to return
        :return: [objectcube.vo.Object], empty set if none found
        """
        raise NotImplementedError()

    def retrieve_by_tag(self, tag, offset=0, limit=10):
        """
        Retrieves all objects tagged with a particular tag
        :param tag: tag to match
        :param offset: the first object to return
        :param limit: the number of objects to return
        :return: [objectcube.vo.Object], empty set if none found
        """
        raise NotImplementedError()
