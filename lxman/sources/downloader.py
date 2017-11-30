import requests
import threading
from colorama import Fore


class Downloader(threading.Thread):

    def __init__(self, uri, target):
        super(Downloader, self).__init__()
        self.uri = uri
        self.target = target
        self.headers = {}

        self.status = lambda:"Download not started yet."
        self.status_data = None

        self.running = False

    def run(self):
        self.running = True

        response = requests.get(self.uri, stream=True, headers=self.headers)
        total_length = int(response.headers.get('content-length'))

        if total_length is not None:
            self.status_data = [0, total_length]
            self.status = self.update_status_progress
        else:
            self.status_data = [0, 0]
            self.status = self.update_status_continuuos

        with self.target:
            for data in response.iter_content(chunk_size=4096):
                self.status_data = [self.status_data[0] + len(data), total_length]
                self.target.write(data)

        self.running = False

    def update_status_progress(self):
        current_amount, total_amount = self.status_data
        progress = 50 * current_amount/total_amount
        full_points = int(progress)
        half_points = 1
        non_full_points = 50 - half_points - full_points

        return "".join([
            Fore.GREEN,
            "%.2f MiB"%(current_amount/1024/1024),
            Fore.WHITE,
            " / ",
            Fore.GREEN,
            "%.2f MiB"%(total_amount/1024/1024),
            Fore.WHITE,
            " [",
            Fore.GREEN,
            "="*full_points,
            Fore.YELLOW,
            ">",
            Fore.WHITE,
            " "*non_full_points,
            "]",
        ])

    def update_status_continuuos(self):
        kbytes = (current_amount//1024)%50
        length_end = 10
        length_start = 0
        empty_end = 0
        if kbytes+length_end > 50:
            length_start = 50 - kbytes
            length_end = 10 - length_start
        else:
            empty_end = 50-kbytes-length_end

        return "".join([
            Fore.GREEN,
            "%.2f MiB"%(current_amount/1024/1024),
            Fore.WHITE,
            " / ",
            Fore.GREEN,
            "%.2f MiB"%(total_amount/1024/1024),
            Fore.WHITE,
            " [",
            Fore.GREEN,
            "="*length_start,
            " "*kbytes,
            "="*length_end,
            " "*empty_end,
            Fore.WHITE,
            "]"
        ])
