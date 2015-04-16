import os
import logging
import cStringIO
import json
import shutil

from objectcube.services.base import BaseBlobService
from objectcube.exceptions import ObjectCubeException
from objectcube.utils import md5_from_stream

logger = logging.getLogger('FileBlobService')

READ_CHUNK_SIZE = 512


class FileBlobService(BaseBlobService):
    def flush(self):
        logging.debug('Calling flush')
        if os.path.exists(os.path.join(self.blob_disk_location)):
            shutil.rmtree(self.blob_disk_location)
        os.makedirs(self.blob_disk_location)

    def __init__(self, *args, **kwargs):
        self.blob_disk_location = os.environ.get('FILESYSTEM_BLOB_DIR',
                                                 'blobs')
        self.flush()

    def _get_blob_path(self, digest):
        return os.path.join(self.blob_disk_location, digest)

    def _get_meta_location(self, digest):
        return os.path.join(self.blob_disk_location, '{0}.{1}'
                            .format(digest, 'meta'))

    def retrieve_uri(self, digest):
        logging.debug('Calling retrieve_uri')
        if self.has(digest):
            return 'file://{}'.format(self._get_blob_path(digest))

        logging.error('No blob with digest found {}'.format(digest))
        raise ObjectCubeException('No blob found by digest {}'.format(digest))

    def retrieve_meta(self, digest):
        if not self.has(digest):
            raise ObjectCubeException('No blob found by digest {}'
                                      .format(digest))

        # Check if we have meta file on disk
        meta_filepath = self._get_meta_location(digest)

        # If not meta has been added, we return empty dict
        if not os.path.exists(meta_filepath):
            return dict()
        with open(meta_filepath, 'r') as fs:
            data = fs.read().strip()
            d = json.loads(data)
            return d

    def get_data(self, digest):
        if not self.has(digest):
            raise ObjectCubeException('waaa')

        blob_path = self._get_blob_path(digest)

        with open(blob_path, "rb") as f:
            data = cStringIO.StringIO(f.read())
            return data

    def add(self, stream, digest=None, meta=None):
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
            meta_filepath = self._get_meta_location(digest)
            with open(meta_filepath, 'w') as fs:
                fs.write(json.dumps(meta))
        return digest

    def has(self, digest):
        return os.path.exists(os.path.join(self.blob_disk_location, digest))
