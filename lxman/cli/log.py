from colorama import Fore
from colorama.ansi import clear_line

class Log(object):

    def __init__(self):
        self.last_type = None

    def _log_raw(self, type, color, msg, prefix="\n"):
        if type != self.last_type and type != "log":
            print()
        self.last_type = type

        print(
            prefix,
            Fore.RESET,
            "[",
            color,
            "*",
            Fore.RESET,
            "] ",
            msg,
            sep="", end=""
        )

    def log(self, msg):
        self._log_raw('log', Fore.GREEN, msg)

    def update(self, msg):
        self._log_raw('update', Fore.CYAN, msg, clear_line() + '\r')
