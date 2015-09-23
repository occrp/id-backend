import os
import io
import shutil
import zipfile
import rarfile
import tempfile
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


def unpacked_fhs(filename):
    """ Given a file name, check if is in a well-known packaging format (e.g.
    ZIP or RAR files) and return an iterator of file handles and file names. If it
    is a simple file, return just one tuple. """
    root, ext = os.path.splitext(filename)
    ext = ext.strip('.').strip().lower()

    extractors = {
        "zip": (zipfile.ZipFile, zipfile.is_zipfile),
        "rar": (rarfile.RarFile, rarfile.is_rarfile),
    }

    if ext in extractors and extractors[ext][1](filename):
        tempdir = tempfile.mkdtemp()
        with extractors[ext][0](filename, 'r') as archive:
            for name in archive.namelist():
                filename = os.path.basename(name).decode('utf-8', 'replace')
                info = archive.getinfo(name)
                if not filename:
                    continue
                if hasattr(info, 'isdir') and info.isdir():
                    continue
                source = archive.open(name)
                tmpfilename = os.path.join(tempdir, filename)
                target = file(tmpfilename, "wb")
                with source, target:
                    shutil.copyfileobj(source, target)
                yield filename, open(tmpfilename, "rb")
                os.remove(tmpfilename)
        shutil.rmtree(tempdir)

    # everything else
    else:
        with open(filename, 'r') as fh:
            yield filename, fh



class BufferedFile(object):
    ''' A buffered file that preserves the beginning of a stream up to
    buffer_size '''
    # from: https://github.com/okfn/messytables/blob/master/messytables/core.py
    # MIT Licensed

    def __init__(self, fp, buffer_size=2048):
        self.data = io.BytesIO()
        self.fp = fp
        self.offset = 0
        self.len = 0
        self.fp_offset = 0
        self.buffer_size = buffer_size

    def _next_line(self):
        try:
            return self.fp.readline()
        except AttributeError:
            return next(self.fp)

    def _read(self, n):
        return self.fp.read(n)

    @property
    def _buffer_full(self):
        return self.len >= self.buffer_size

    def readline(self):
        if self.len < self.offset < self.fp_offset:
            raise BufferError('Line is not available anymore')
        if self.offset >= self.len:
            line = self._next_line()
            self.fp_offset += len(line)

            self.offset += len(line)

            if not self._buffer_full:
                self.data.write(line)
                self.len += len(line)
        else:
            line = self.data.readline()
            self.offset += len(line)
        return line

    def read(self, n=-1):
        if n == -1:
            # if the request is to do a complete read, then do a complete
            # read.
            self.data.seek(self.offset)
            return self.data.read(-1) + self.fp.read(-1)

        if self.len < self.offset < self.fp_offset:
            raise BufferError('Data is not available anymore')
        if self.offset >= self.len:
            byte = self._read(n)
            self.fp_offset += len(byte)

            self.offset += len(byte)

            if not self._buffer_full:
                self.data.write(byte)
                self.len += len(byte)
        else:
            byte = self.data.read(n)
            self.offset += len(byte)
        return byte

    def tell(self):
        return self.offset

    def seek(self, offset):
        if self.len < offset < self.fp_offset:
            raise BufferError('Cannot seek because data is not buffered here')
        self.offset = offset
        if offset < self.len:
            self.data.seek(offset)
