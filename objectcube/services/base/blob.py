from service import Service


class BaseBlobService(Service):
    """
    Base class for blob services. The purpose of this service is to mange
    uploads and uri handling for blob objects in the ObjectCube model.

    The implementation decides where the blobs are stored and what metadata
    is kept with each blob. Implementations could be storing files on
    file system, AWS-S3, Swift, etc.

    Blobs are identified by MD5 checksums. This allows us to reuse objects
    without duplicating them.
    """
    def add(self, stream, meta=None, digest=None):
        """
        :param stream:
        :param meta:
        :param digest:
        :return: digest
        """
        raise NotImplementedError()

    def has(self, digest):
        """

        :param digest:
        :return:
        """
        raise NotImplementedError()

    def retrieve_uri(self, digest):
        """

        :param digest:
        :return:
        """
        raise NotImplementedError()

    def retrieve_meta(self, digest):
        """

        :param digest:
        :return:
        """
        raise NotImplementedError()

    def get_data(self, digest):
        """

        :param digest:
        :return:
        """
        raise NotImplementedError()

    def flush(self):
        """

        :return:
        """
        raise NotImplementedError()
