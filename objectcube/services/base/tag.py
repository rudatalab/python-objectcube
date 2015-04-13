from service import Service


class BaseTagService(Service):
    def retrieve(self, offset=0, limit=10):
        """
        Retrieves tags from data store.
        :param offset: The offset value for the result.
        :param limit: The limit value for the result.
        :return: List of Tag objects.
        """
        raise NotImplementedError()

    def add(self, tag):
        """
        Adds new tag to data store.
        :param tag: Tag object filled with data. Note that the id field must
        be set to None when creating new tag.
        :return: Returns the newly created tag object. It is the same tag
        object passed in by parameter, with updated id value.
        """
        raise NotImplementedError()

    def update(self, tag):
        """
        Updates existing data store tag to match given tag.
        :param tag: Tag object to update. Note that the id field must
        be set to valid id of existing data store tag.
        :return: Returns the updated tag object as seen by the data store
        after update.
        """

    def delete(self, tag):
        """
        Deletes existing data store tag.
        :param tag: Tag object to delete. Note that the id field must
        be set to valid id of existing data store tag.
        :return: Returns nothing.
        """

    def count(self):
        """
        Returns the count of all tags in data store. Note that this value might
        not be accurate. This value should be thought of as estimate
        of the tag count.
        :return: Integer
        """
        raise NotImplementedError()

    def retrieve_by_id(self, _id):
        """
        Retrieves tag by id.
        :param _id: Id for a given Tag.
        :return: Tag object if found, None otherwise
        """
        raise NotImplementedError()

    def retrieve_by_value(self, value):
        """
        Retrieves tags by value.
        :param value: Value to fetch.
        :return: List of tag objects, or empty list if none are found.
        """
        raise NotImplementedError()

    def retrieve_by_plugin(self, plugin, offset=0, limit=100):
        """
        Retrieves tags by plugin.
        :param plugin:
        :param offset:
        :param limit:
        :return:
        """
        raise NotImplementedError()

    def retrieve_by_concept(self, concept):
        """
        Retrieves tags by concept.
        :param concept: Concept to fetch.
        :return: List of tag objects, or empty list if none are found.
        """
        raise NotImplementedError()

    def retrieve_or_create(self, tag):
        """
        Retrieves tag matching value, plugin_id and concept from the data store
        or creates a new tag if not found. If retrieval is ambiguous an
        ObjectCubeException
        is thrown.
        :param tag: Tag object to retrieve or create. Note that the id field is
        ignored.
        :return: A Tag from populated from data store, either existing one
        or a newly created one.
        """
        raise NotImplementedError()
