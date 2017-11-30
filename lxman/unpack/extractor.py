from lxman.vendor.ntfsea import ntfsea

class Extractor(object):
    EXTRACTORS = []

    def __init__(self, sources, update=None):
        self.sources = sources
        self.update = update

    def extract(self, directory):
        for _ in self.iter_extract(directory): pass

    def iter_extract(self, directory):
        ntfsea.init()

        for source in self.sources:
            yield source
            self.extract_archive(source, directory)

    @classmethod
    def register(cls, subcls):
        cls.EXTRACTORS.append(subcls)
        return subcls

    @classmethod
    def _find_extractor(cls, *pathes, update=None):
        current_pathes = []
        last_extractor = None

        for path in pathes:
            for extractor in cls.EXTRACTORS:
                if extractor.can_extract(path):
                    if last_extractor is not None and last_extractor != extractor:
                        yield last_extractor(current_pathes, update)
                        current_pathes = []

                    last_extractor = extractor
                    current_pathes.append(path)

        if last_extractor is not None:
            yield last_extractor(current_pathes, update)

    @classmethod
    def find_extractor(cls, *pathes, update=None):
        return MultiExtractor(
            list(cls._find_extractor(*pathes, update=update)),
            update=update
        )


class MultiExtractor(Extractor):

    def iter_extract(self, directory):
        for source in self.sources:
            yield from source.iter_extract(directory)
