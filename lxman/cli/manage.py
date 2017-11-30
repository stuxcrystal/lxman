import os
import sys
import shutil

import click
from colorama import Fore

from lxman.unpack import Extractor
from lxman.sources import Source
from lxman.registry import Lxss, Distribution
from lxman.cli.settings import Dist
from lxman.cli.page import Page
from lxman.cli.log import Log


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


@click.group()
def manage():
    pass


@manage.command('delete')
@click.argument('distribution', type=Dist)
@click.option("--yes", is_flag=True, callback=abort_if_false, expose_value=False,
                      prompt="Are you sure to delete the distribition?")
def delete(distribution):
    if distribution.guid == Lxss.default.guid:
        print(Fore.RED + "You are not allowed to delete a default distribition")
        sys.exit(2)
    distribution.delete()

@manage.command('create')
@click.argument('distribution', type=str, required=True)
@click.argument('target', type=click.Path(
    exists=True,
    readable = True,
    resolve_path = True,
    file_okay = False,
    dir_okay = True,
), required=True)
@click.option('--raw', is_flag=True)
@click.option("--allow-duplicate-name", is_flag=True)
def create(distribution, target, raw, allow_duplicate_name):
    if not allow_duplicate_name and Lxss.get(distribution) is not None:
        print(Fore.RED + "A distribution with this name already exists")
        sys.exit(2)

    distribution = Distribution.create(distribution, target)

    pg = Page(distribution.name)
    pg.push('name', distribution.name)
    pg.push('guid', distribution.guid)
    pg.push('base-path', distribution.base_path)
    pg.output(raw=raw)


@manage.command('lock')
@click.argument('distribution', type=Dist, default=Lxss.default)
def lock(distribution):
    distribution.state = 3

@manage.command('unlock')
@click.argument('distribution', type=Dist, default=Lxss.default)
def unlock(distribution):
    distribution.state = 1


@manage.command("clean")
@click.option("--yes", is_flag=True, callback=abort_if_false, expose_value=False,
                      prompt="Are you sure to delete the rootfs?")
@click.option("--root", is_flag=True)
@click.argument('distribution', type=Dist, default=Lxss.default)
def clean(distribution, root):
    path = distribution.base_path
    if os.path.exists(os.path.join(path, 'rootfs')):
        root = True

    if os.path.exists(path):
        shutil.rmtree(path)
    else:
        root = True

    import time
    time.sleep(2)
    os.makedirs(path, exist_ok=True)
    if root:
        os.mkdir(os.path.join(path, 'rootfs'))
        os.mkdir(os.path.join(path, 'temp'))


@manage.command('unpack')
@click.argument('distribution', type=Dist, default=Lxss.default)
@click.argument('source', type=str)
def unpack(distribution, source):
    log = Log()
    sources = Source.find(source)
    sources.retrieve(update=log.update, log=log.log)
    try:
        extractor = Extractor.find_extractor(*sources.sources(), update=log.update)
        target = distribution.base_path

        if os.path.exists(os.path.join(target, 'rootfs')):
            target = os.path.join(target, 'rootfs')

        for file in extractor.iter_extract(target):
            log.log(Fore.RESET + "Extracting: " + Fore.CYAN + file)
    finally:
        log.log("Cleaning up temporary files")
        sources.cleanup()
