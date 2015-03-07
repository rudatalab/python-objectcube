import cStringIO

from objectcube.factory import get_service
from objectcube.utils import md5_from_stream
from base import ObjectCubeTestCase


class TestObjectService(ObjectCubeTestCase):
    def __init__(self, *args, **kwargs):
        super(TestObjectService, self).__init__(*args, **kwargs)
        self.blob_service = get_service('BlobService')

    def tearDown(self):
        self.blob_service.flush()

    def create_stream_with_random_data(self):
        stream = cStringIO.StringIO('some data')
        digest = md5_from_stream(stream)
        return digest, stream,

    def test_add_new_blob(self):
        digest, stream = self.create_stream_with_random_data()

        self.blob_service.add_blob(stream, digest=digest)
        self.assertTrue(self.blob_service.has_blob(digest),
                        msg='When blob is added, calling has_blob on '
                            'its digest should return True')

    def test_has_blob(self):
        self.assertFalse(self.blob_service.has_blob('foobar'),
                         msg='When no blob has been added with a given '
                             'checksum, has_blob should return False')

        digest, stream = self.create_stream_with_random_data()
        self.blob_service.add_blob(stream, digest=digest)

        self.assertTrue(self.blob_service.has_blob(digest),
                        msg='When blob has been added with a given digest, '
                            'has_blob should return True')

    def test_get_uri(self):
        digest, stream = self.create_stream_with_random_data()
        self.assertIsNone(self.blob_service.get_uri(digest),
                          msg='When URI is requested for digest that '
                              'has not been added, get_uri should return None')

        self.blob_service.add_blob(stream, digest=digest)

        self.assertIsNotNone(self.blob_service.get_uri(digest),
                             msg='When URI is requested for digest that '
                                 'has been added, get_uri should '
                                 'return a value')