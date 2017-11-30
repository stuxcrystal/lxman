import os
import tarfile
from collections import OrderedDict

from colorama import Fore

from lxman.unpack.extractor import Extractor
from lxman.vendor.ntfsutils import escape_ntfs_invalid
from lxman.vendor.ntfsea import ntfsea, lxattrb, stmode


tarfile.TarFile.OPEN_METH = OrderedDict()
tarfile.TarFile.OPEN_METH['gz']  = 'gzopen'
tarfile.TarFile.OPEN_METH['bz2'] = 'bz2open'
tarfile.TarFile.OPEN_METH['xz']  = 'xzopen'
tarfile.TarFile.OPEN_METH['tar'] = 'taropen'


@Extractor.register
class TarExtractor(Extractor):

    def __init__(self, images=(), update=None):
        self.sources = list(images)
        self.update = update

    @classmethod
    def can_extract(self, path):
        try:
            with open(path, 'rb') as raw_file:
                with tarfile.open(fileobj=raw_file, mode='r:*') as tf:
                    f = tf.next()
                    if f is not None:
                        return True
        except PermissionError:
            return False
        return False

    def extract_archive(self, image, directory):
        with open(image, 'rb') as raw_file:
            with tarfile.open(
                    fileobj=raw_file,
                    mode='r:*',
                    dereference=True,
                    ignore_zeros=True,
                    errorlevel=2) as tf:
                f = tf.next()
                if f is None:
                    raise FileNotFoundError("Failed to extract archive")

                while f is not None:
                    self.extract_file(tf, f, directory)
                    f = tf.next()

    def extract_file(self, tar, file, directory):
        if file.isdev():
            return

        if self.update is not None:
            self.update(Fore.WHITE + "Extracting: " + Fore.CYAN + file.name)

        file.name = self.tar_path(file, directory)

        if file.issym() or file.islnk():
            self.extract_link(file, directory)
        elif file.isdir():
            oldname = file.name
            file.name = file.name + "\\$dummy"
            self.create_parents(file)
            file.name = oldname
        else:
            tar.extract(file, directory)

        path = self.tar_path(file, directory)
        os.chmod(path, 0o777)
        attrb = lxattrb.fromtar(file).generate()
        ntfsea.writeattr(path, 'lxattrb', attrb)

    def extract_link(self, file, directory):
        self.create_parents(file)
        with open(file.name, 'w', encoding='utf-8') as link:
            link.write(file.linkname.lstrip('.') if file.islnk() else file.linkname)

    def tar_path(self, file, directory):
        name = file.name
        if file.name.startswith("./"):
            name = name[2:]
        return escape_ntfs_invalid(os.path.join(directory, name))

    def create_parents(self, file):
        dirname = os.path.dirname(file.name)
        if not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)
