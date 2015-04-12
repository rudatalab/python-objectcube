import os
import shutil
import logging
from objectcube.services.base import BaseBlobService
from objectcube.utils import md5_from_stream

FILE_BLOB_SERVICE_PATH = 'shared/data'
READ_CHUNK_SIZE = 512
logger = logging.getLogger('FileBlobServiceImpl')


class FileBlobServiceImpl(BaseBlobService):
    def __init__(self):
        if not os.path.exists(FILE_BLOB_SERVICE_PATH):
            os.makedirs(FILE_BLOB_SERVICE_PATH)

    def get_blob_meta(self, digest):
        pass

    def flush(self):
        if os.path.exists(FILE_BLOB_SERVICE_PATH):
            shutil.rmtree(FILE_BLOB_SERVICE_PATH)
            os.mkdir(FILE_BLOB_SERVICE_PATH)

    def get_uri(self, digest):
        if os.path.exists(os.path.join(FILE_BLOB_SERVICE_PATH, digest)):
            return os.path.join(FILE_BLOB_SERVICE_PATH, digest)

    def add_blob(self, fs, blob_meta=None, digest=None):
        fs.seek(0)

        if not blob_meta:
            blob_meta = {}

        if not digest or not blob_meta.get('digest'):
            logger.debug('No digest added as parameter. '
                         'Calculating digest from the stream')
            digest = md5_from_stream(fs)

        blob_path = os.path.join(FILE_BLOB_SERVICE_PATH, digest)

        # If the file already exists, we don't need to create it again.
        if os.path.exists(blob_path):
            logger.debug('File {} already exist, not creating'
                         .format(blob_path))
            return

        with open(os.path.join(blob_path), 'w+b') as file_fs:
            data = fs.read(READ_CHUNK_SIZE)
            while data:
                data = fs.read(READ_CHUNK_SIZE)
                file_fs.write(data)

    def has_blob(self, digest_id):
        return os.path.exists(os.path.join(FILE_BLOB_SERVICE_PATH, digest_id))