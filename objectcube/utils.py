import hashlib


def md5_for_file(f, block_size=2**20):
    f.seek(0)
    md5 = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)
    f.seek(0)
    return md5.hexdigest()
