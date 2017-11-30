import re
import os
import time
import tempfile

import requests
from colorama import Fore

from lxman.sources.source import Source
from lxman.sources.downloader import Downloader


@Source.register
class DockerSource(Source):
    TAG_RE = re.compile(r"^(?P<IMAGE>([^/]+/)?[^:\\/]+)(:(?P<TAG>[^/\\]+))?$")

    def __init__(self, image):
        self.image = image
        self.files = []
        self.downloaded = []
        self.state = None

        self.token = None
        self.expire = None

    @classmethod
    def can_use(cls, uri):
        return cls.TAG_RE.match(uri) is not None

    def parse_image(self):
        img_info = self.TAG_RE.match(self.image).groupdict()
        if img_info['TAG'] is None:
            img_info['TAG'] = 'latest'
        if '/' not in img_info['IMAGE']:
            img_info['IMAGE'] = 'library/' + img_info['IMAGE']
        return img_info

    def retrieve(self, update=None, log=(lambda m:None)):
        img_info = self.parse_image()
        log(Fore.GREEN + "Fetching " + Fore.CYAN + img_info['IMAGE'] + ':' + img_info['TAG'])
        self._retrieve_token(log)

        path = 'https://registry.hub.docker.com/v2/%s/manifests/%s' % (
            img_info['IMAGE'],
            img_info['TAG']
        )
        with requests.get(path, headers={
                'authorization': self.token,
                'content-type': 'application/json'
        }) as r:
            manifest = r.json()
            if not len(manifest['fsLayers']):
                log(Fore.RED + "This image does not contain a layer")
                return

        for layer in manifest['fsLayers']:
            self._download_layer(layer, update, log)

    def _download_layer(self, layer, update, log):
        if layer['blobSum'] in self.downloaded:
            return
        self.downloaded.append(layer['blobSum'])

        img_info = self.parse_image()

        log(Fore.RESET + "Downloading: " + Fore.YELLOW + layer['blobSum'])
        self._retrieve_token(log)

        path = tempfile.NamedTemporaryFile(delete=False, suffix='.tar.gz')
        self.files.append(path.name)
        with path:
            uri = "https://registry.hub.docker.com/v2/%s/blobs/%s" % (
                img_info['IMAGE'],
                layer['blobSum']
            )
            download = Downloader(uri, path)
            download.headers['authorization'] = self.token
            download.start()

            while download.running:
                if update is not None:
                    update(download.status())
                time.sleep(1)

            update("Download completed")

    def _retrieve_token(self, log):
        if self.expire is not None and time.time() <= self.expire:
            return

        img_info = self.parse_image()

        log(Fore.CYAN + "Requesting Authentication Token for Docker")
        with requests.get('https://auth.docker.io/token?service=registry.docker.io&scope=repository:%s:pull' % img_info['IMAGE']) as f:
            data = f.json()
            self.token = "Bearer " + data['token']
            self.expire = time.time() + data['expires_in']

    def sources(self):
        return list(reversed(self.files))

    def cleanup(self):
        for file in self.files:
            os.remove(file)
