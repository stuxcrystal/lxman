import os
import shutil

from colorama import Fore

from lxman.unpack.extractor import Extractor
from lxman.vendor.ntfsea import ntfsea, lxattrb, stmode


@Extractor.register
class DirExtractor(Extractor):

    @classmethod
    def can_extract(cls, name):
        return os.path.isdir(name)

    def extract_archive(self, source, target):
        if os.path.exists(os.path.join(source, "rootfs")):
            source = os.path.join(source, "rootfs")

        for path, dirs, files in os.walk(source):
            relpath = os.path.relpath(path, source)
            self.update(Fore.RESET + "Extracting: " + Fore.CYAN + relpath)
            newabs = os.path.join(target, relpath)

            if not os.path.exists(newabs):
                os.mkdir(newabs, 0o777)
            else:
                os.chmod(newabs, 0o777)
            self.copy_attributes(path, newabs)

            for file in files:
                self.update(Fore.RESET + "Extracting: " + Fore.CYAN + os.path.join(relpath, file))
                self.copy_file(os.path.join(path, file), os.path.join(newabs, file))

    def copy_file(self, src, dst):
        shutil.copyfile(src, dst)
        os.chmod(dst, 0o777)
        self.copy_attributes(src, dst)

    def copy_attributes(self, src, dst):
        lxattrb = ntfsea.getattr(src, 'lxattrb')
        ntfsea.writeattr(dst, 'lxattrb', lxattrb)
