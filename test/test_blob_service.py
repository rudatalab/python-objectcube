import unittest
import cStringIO
from objectcube.exceptions import ObjectCubeException
from objectcube.utils import md5_from_stream

from objectcube.factory import get_service


class TestBlobService(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestBlobService, self).__init__(*args, **kwargs)
        self.blob_service = get_service('BlobService')

    def setUp(self):
        self.blob_service.flush()

    def test_retrieve_uri_raises_if_blob_is_not_found(self):
        with self.assertRaises(ObjectCubeException):
            self.blob_service.retrieve_uri('nothing')

    def test_retrieve_uri_returns_string_uri_if_blob_is_found(self):
        data = cStringIO.StringIO('test file data')
        digest = md5_from_stream(data)
        self.blob_service.add(data, digest=digest)
        uri = self.blob_service.retrieve_uri(digest)

        self.assertIsNotNone(uri)
        self.assertEqual(type(uri), str)

    def test_retrieve_meta_raises_when_blob_not_found(self):
        with self.assertRaises(ObjectCubeException):
            self.blob_service.retrieve_meta('nothing')

    def test_retrieve_meta_returns_empty_dict_when_no_meta_added(self):
        data = cStringIO.StringIO('test file data')
        digest = md5_from_stream(data)
        self.blob_service.add(data, digest=digest)
        self.assertEqual(self.blob_service.retrieve_meta(digest), {})

    def test_retrieve_meta_returns_meta_when_added(self):
        data = cStringIO.StringIO('test file data')
        digest = md5_from_stream(data)
        expected_meta = {
            'content-type': 'application/json',
            'file-size': 20
        }
        self.blob_service.add(data, meta=expected_meta)
        actual_meta = self.blob_service.retrieve_meta(digest)
        self.assertEqual(expected_meta, actual_meta)

    def test_get_data_raises_if_blob_not_found(self):
        with self.assertRaises(ObjectCubeException):
            self.blob_service.get_data('nothing')

    def test_get_data_returns_data_if_added(self):
        data = cStringIO.StringIO('some-data')
        digest = self.blob_service.add(data)
        actual_data = self.blob_service.get_data(digest)
        self.assertEqual(md5_from_stream(actual_data), digest)

    def test_add_returns_correct_digest_when_digest_is_not_given(self):
        data = cStringIO.StringIO('some-data')
        actual_digest = md5_from_stream(data)
        expected_digest = self.blob_service.add(data)
        self.assertEqual(actual_digest, expected_digest)

    def test_add_returns_correct_digest_when_digest_is_added(self):
        data = cStringIO.StringIO('some-data')
        actual_digest = md5_from_stream(data)
        expected_digest = self.blob_service.add(data, digest=actual_digest)
        self.assertEqual(actual_digest, expected_digest)

    def test_has_returns_false_when_blob_has_not_been_added(self):
        self.assertFalse(self.blob_service.has('foobar'))

    def test_has_returns_true_when_blob_has_not_been_added(self):
        data = cStringIO.StringIO('some-data')
        digest = self.blob_service.add(data)
        self.assertTrue(self.blob_service.has(digest))
