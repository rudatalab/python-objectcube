from service import Service


class BaseObjectService(Service):
    def add(self, _object):
        """
        Add object to data store.
        :param _object: Instance of objectcube.vo.Object.
        :return: objectcube.vo.Object.
        """
        raise NotImplementedError()

    def count(self):
        """
        Counts the number of objects in data store. Note that this value
        might not be accurate
        :return: Number of objects as number
        """
        raise NotImplementedError()

    def update(self, _object):
        """
        Updates a given object
        :param _object: Instance of objectcube.vo.Object.
        :return: Instance of objectcube.vo.Object.
        """
        raise NotImplementedError()

    def delete(self, _object):
        """
        Deletes a given object that has been added.
        :param _object: Instance of objectcube.vo.Object.
        :return: None
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
        """

        :param offset:
        :param limit:
        :return:
        """
        raise NotImplementedError()

    def retrieve_by_tag(self, tag, offset=0, limit=10):
        """

        :param tag:
        :param offset:
        :param limit:
        :return:
        """
        raise NotImplementedError()
