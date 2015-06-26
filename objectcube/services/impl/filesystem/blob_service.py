import os
import cStringIO
import json
import shutil

from objectcube.services.base import BaseBlobService
from objectcube.exceptions import ObjectCubeException
from objectcube.utils import md5_from_stream
from logging import getLogger

READ_CHUNK_SIZE = 512


class FileBlobService(BaseBlobService):
    def __init__(self):
        super(FileBlobService, self).__init__()
        self.logger = getLogger('FileBlobService')
        self.blob_disk_location = os.environ.get('FILESYSTEM_BLOB_DIR',
                                                 'blobs')
        self.flush()

    def flush(self):
        self.logger.debug('flush()')
        if os.path.exists(os.path.join(self.blob_disk_location)):
            shutil.rmtree(self.blob_disk_location)
        os.makedirs(self.blob_disk_location)

    def _get_blob_path(self, digest):
        return os.path.join(self.blob_disk_location, digest)

    def _get_meta_location(self, digest):
        return os.path.join(self.blob_disk_location, '{0}.{1}'
                            .format(digest, 'meta'))

    def retrieve_uri(self, digest):
        self.logger.debug('has(): %s', repr(digest))
        if self.has(digest):
            return 'file://{}'.format(self._get_blob_path(digest))

        raise ObjectCubeException('No blob found by digest')

    def retrieve_meta(self, digest):
        self.logger.debug('retrieve_meta(): %s', repr(digest))
        if not self.has(digest):
            raise ObjectCubeException('No blob found by digest {}'
                                      .format(digest))

        # Check if we have meta file on disk
        meta_file_path = self._get_meta_location(digest)

        # If not meta has been added, we return empty dict
        if not os.path.exists(meta_file_path):
            return dict()
        with open(meta_file_path, 'r') as fs:
            data = fs.read().strip()
            d = json.loads(data)
            return d

    def get_data(self, digest):
        self.logger.debug('get_data(): %s', repr(digest))
        if not self.has(digest):
            raise ObjectCubeException('Function requires valid digest')

        blob_path = self._get_blob_path(digest)

        with open(blob_path, "rb") as f:
            data = cStringIO.StringIO(f.read())
            return data

    def add(self, stream, digest=None, meta=None):
        self.logger.debug('add(): %s / %s / %s',
                          repr(stream), repr(digest), repr(meta))
        if not digest:
            digest = md5_from_stream(stream)

        if self.has(digest):
            return digest

        blob_path = os.path.join(self.blob_disk_location, digest)

        with open(os.path.join(blob_path), 'wb') as file_fs:
            data = stream.read(READ_CHUNK_SIZE)
            while data:
                file_fs.write(data)
                data = stream.read(READ_CHUNK_SIZE)

        if meta:
            meta_file_path = self._get_meta_location(digest)
            with open(meta_file_path, 'w') as fs:
                fs.write(json.dumps(meta))
        return digest

    def has(self, digest):
        self.logger.debug('has(): %s', repr(digest))
        return os.path.exists(os.path.join(self.blob_disk_location, digest))
