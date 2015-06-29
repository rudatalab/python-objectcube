from service import Service


class BaseConceptService(Service):
    def count(self):
        """
        Counts the number of objects in data store.
        Note that this value may not be accurate
        :return: Number of Concept in database as number
        """
        raise NotImplementedError()

    def add(self, concept):
        """
        Adds new concept to data store
        :param: concept: instance of Concept to add
        :return: added concept
        """
        raise NotImplementedError()

    def update(self, concept):
        """
        Updates the given concept
        :param concept: instance of Concept to update
        :return: updated concept
        """
        raise NotImplementedError()

    def delete_by_id(self, id_):
        """
        Deletes a concept with given id from the database
        :param: id_: id of Concept to delete
        :return: None, raises exception if none found
        """
        raise NotImplementedError()

    def delete(self, concept):
        """
        Deletes a given concept from the database
        :param: concept: instance of Concept to delete
        :return: None, raises exception if none found
        """
        raise NotImplementedError()

    def retrieve_or_create(self, concept):
        """
        Retrieves a given concept if it exists.
        If it does not exist a new concept is created and returned.
        :param: concept: instance of Concept to add
        :return: existing or added concept
        """
        raise NotImplementedError()

    def retrieve_by_id(self, id_):
        """
        Retrieves a given concept by id
        :param: id_: the identifier of the Concept
        :return: Concept if found, None otherwise
        """
        raise NotImplementedError()

    def retrieve_by_title(self, title):
        """
        Fetches Concept by id.
        :param: title: Title for a given Concept.
        :return: Returns a Concept if found by a given title, None otherwise.
        """
        raise NotImplementedError()

    def retrieve(self, offset=0L, limit=10L):
        """
        Retrieves all concepts in database
        :param: offset: the first concepts to return
        :param: limit: the number of concepts to return
        :return: [Concept], empty set if none found
        """
        raise NotImplementedError()

    def retrieve_by_regex(self, title=None, description=None,
                          offset=0L, limit=10L):
        """
        Retrieves a given object by regex on name and/or description
        :param: title: regular expression to match on name
        :param: description: regular expression to match on description
        :param: offset: the first object to return
        :param: limit: the number of objects to return
        :return: [Concept], empty set if none found
        """
        raise NotImplementedError()
