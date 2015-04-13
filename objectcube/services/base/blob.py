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

    def has_blob(self, digest_id):
        """
        Checks if a given blob digest id has been added.
        :param digest_id: Digest sum for a content of a given file.
        :return: True if blob has been added, false otherwise.
        """
        raise NotImplementedError()

    def add_blob(self, fs, blob_meta, digest=None):
        """
        Adds a give blob.
        :param fs: Stream to file, or memory.
        :param blob_meta: Dictionary of meta-data that should be stored
        with the blob (size, content-type, etc)
        :param digest: Digest of the sum. This field is optional. If not
        provided then md5 will be calculated on the fs.
        :return: None
        """
        raise NotImplementedError()

    def get_uri(self, digest):
        """
        Returns URI to the blob. This can vary by implementations. For
        filesystem implementation this could we the path to the file or for
        Swift, this can be a temporary URL to the blob.
        :param digest: Digest of blob that has been added.
        :return: URI string if blob has been added, None otherwise.
        """
        raise NotImplementedError()

    def flush(self):
        """
        Flushes all blobs that have been added.
        :return: None
        """
        raise NotImplementedError()

    def get_blob_meta(self, digest):
        """
        Fetch blob meta data, if added, for a given blob.
        :param digest: Digest for a blob that has been added.
        :return: Dictionary with meta-data if found, None otherwise.
        """
        raise NotImplementedError()
