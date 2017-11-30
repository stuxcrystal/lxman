import os
import click

from colorama import Fore

from lxman.cli.log import Log
from lxman.vendor.ntfsea import ntfsea, lxattrb, stmode


@click.group()
def fs():
    pass

@fs.command("fix")
@click.argument("path", type=click.Path(
    exists=True,
    readable = True,
    resolve_path = True,
    file_okay = True,
    dir_okay = True,
), required=True)
@click.option("--file-mode", type=str, default="755")
@click.option("--dir-mode", type=str, default="755")
def fix(path, file_mode, dir_mode):
    ntfsea.init()

    dattrb = lxattrb(stmode.FDIR | int(dir_mode, 8)).generate()
    fattrb = lxattrb(stmode.FREG | int(file_mode, 8)).generate()

    log = Log()
    if os.path.exists(os.path.join(path, "rootfs")):
        log.log("Instance-Root detected. Only looking at rootfs.")
        path = os.path.join(path, "rootfs")

    def fix(file):
        if ntfsea.getattr(file, 'lxattrb') is not None:
            log.update(Fore.GREEN + file)
            return
        log.log("Fixed: " + Fore.RED + file)

        if os.path.isdir(path):
            attrb = dattrb
        else:
            attrb = fattrb

        ntfsea.writeattr(path, 'lxattrb', attrb)


    log.log("Fixing missing linux-attributes in " + Fore.CYAN + path)
    if not os.path.isdir(path):
        fix(path)
        log.log("Single file fixed.")
        return

    for dirpath, dirs, files in os.walk(path):
        fix(dirpath)
        for file in files:
            fix(os.path.join(dirpath, file))
