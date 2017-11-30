from colorama import Fore
import json


class Page(object):

    def __init__(self, title):
        self.title = title
        self.table = []

    def push(self, name, value):
        self.table.append((name, value))

    def output(self, raw=False):
        if raw:
            print(self.json())
        else:
            self.echo()

    def echo(self):
        print(Fore.GREEN + self.title)
        print(Fore.GREEN + ('-'*len(self.title)))

        if len(self.table) > 0:
            max_tbl_length = len(max(self.table, key=lambda s:len(s[0]))[0])
        else:
            max_tbl_length = 0

        for k, v in self.table:
            k = str(k).ljust(max_tbl_length)
            prefix = Fore.CYAN + k + Fore.RESET + ' : '
            if v is None:
                print(prefix + Fore.RED + '<None>')
            elif isinstance(v, (list, tuple)):
                length = max_tbl_length + 3
                for sv in v:
                    print(prefix + Fore.CYAN + str(sv))
                    prefix = ' ' * length
            else:
                print(prefix + Fore.CYAN + str(v))


    def json(self):
        return json.dumps(dict(self.table))
