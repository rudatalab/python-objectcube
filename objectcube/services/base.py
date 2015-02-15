class BaseTagService(object):
    def get_tags(self, offset=0, limit=10):
        """

        :param offset:
        :param limit:
        :return:
        """
        raise NotImplementedError()

    def add_tag(self, tag):
        """

        :param tag:
        :return:
        """
        raise NotImplementedError()

    def count(self):
        """

        :return:
        """
        raise NotImplementedError()

    def get_by_id(self, _id):
        """

        :param _id:
        :return:
        """
        raise NotImplementedError()

    def get_by_value(self, value):
        """

        :param value:
        :return:
        """
        raise NotImplementedError()