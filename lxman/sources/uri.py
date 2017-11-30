import os
import time
import tempfile
from colorama import Fore

from lxman.sources.source import Source
from lxman.sources.downloader import Downloader


@Source.register
class UriSource(Source):

    def __init__(self, uri):
        self.uri = uri
        self.file = None
        self.state = None

    @classmethod
    def can_use(self, uri):
        return "://" in uri

    def retrieve(self, update=None, log=(lambda m:None)):
        self.path = tempfile.NamedTemporaryFile(delete=False)
        download = Downloader(self.uri, self.path)
        download.start()

        log(Fore.GREEN + f"Downloading {self.uri}")

        while download.running:
            if update is not None:
                update(download.status())
            time.sleep(1)

        log(Fore.GREEN + f"Download complete {self.uri}")

    def sources(self):
        return [self.path.name]

    def cleanup(self):
        os.remove(self.path.name)
