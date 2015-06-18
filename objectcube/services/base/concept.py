from service import Service


class BaseConceptService(Service):
    def count(self):
        """
        Returns approximation of number of concepts in data store.
        :return: Number
        """
        raise NotImplementedError()

    def add(self, concept):
        """
        Adds new concept to data store.
        :param concept: Concept object.
        :return: Updated Concept object.
        """
        raise NotImplementedError()

    def update(self, concept):
        """
        Update concept in data store.
        :param concept: Concept object. Note that this object must have
        a valid id.
        :return: Updated Concept object.
        """
        raise NotImplementedError()

    def delete(self, concept):
        """
        Delete concept object from data store.
        :param concept: Concept object
        that will be deleted.
        :return: None
        """
        raise NotImplementedError()

    def retrieve_or_create(self, concept):
        """
        Retrieves a given concept if it exists, if not new concept is
         created and returned.
        :param concept: Concept object.
        :return: Concept object.
        """
        raise NotImplementedError()

    def retrieve_by_id(self, concept_id):
        """
        Fetches Concept by id.
        :param concept_id: Number
        :return: Returns Concept by given id if found, otherwise None.
        """
        raise NotImplementedError()

    def retrieve(self, offset=0, limit=10):
        """
        Fetches list of concepts, by offset and limit, in data store.
        :param offset: Offset value
        :param limit: Limit value
        :return: List of concepts.
        """
        raise NotImplementedError()

    def retrieve_by_title(self, concept_title, offset=0, limit=10):
        """
        Fetches Concept by id.
        :param concept_title: Title for a given concept.
        :return: Returns a Concept if found by a given title, None otherwise.
        """
        raise NotImplementedError()
