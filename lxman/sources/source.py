

class Source(object):
    SOURCES = []

    @classmethod
    def can_use(cls, source):
        return False

    @classmethod
    def register(cls, subcls):
        cls.SOURCES.append(subcls)
        return subcls

    @classmethod
    def find(cls, path):
        for source in cls.SOURCES:
            if source.can_use(path):
                return source(path)
        return source
