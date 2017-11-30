import os
from lxman.sources.source import Source

@Source.register
class FileSource(Source):

    def __init__(self, path):
        self.path = path

    @classmethod
    def can_use(self, path):
        if '://' in path:
            return False

        return os.path.exists(path)

    def retrieve(self, update=None, log=None):
        pass

    def sources(self):
        return [self.path]

    def cleanup(self):
        pass
