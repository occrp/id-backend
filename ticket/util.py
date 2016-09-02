from hashlib import sha256
from django.utils.text import Truncator


def truncate_summary(text):
    """Truncate a ticket summary."""
    tronc = Truncator(text)
    return tronc.chars(140)


def sha256sum_fh(fh, blocksize=65536):
    hash = sha256()
    for block in iter(lambda: fh.read(blocksize), ""):
        hash.update(block)

    fh.seek(0)
    return hash.hexdigest()
