from hashlib import sha256


def sha256sum(filename, blocksize=65536):
    f = None
    if type(filename) in [str, unicode]:
        f = open(filename, "rb")
    else:
        f = filename

    hash = sha256()
    for block in iter(lambda: f.read(blocksize), ""):
        hash.update(block)

    f.seek(0)
    return hash.hexdigest()
