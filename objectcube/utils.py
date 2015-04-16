import hashlib
from hashlib import md5


def md5_from_stream(f, block_size=2**20):
    f.seek(0)
    digest = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        digest.update(data)
    f.seek(0)
    return digest.hexdigest()


def md5_from_value(value):
    h = md5()
    h.update(str(value))
    return h.hexdigest()
