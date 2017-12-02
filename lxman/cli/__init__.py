import sys
import click
import colorama

from lxman.cli import config
from lxman.cli import manage
from lxman.cli import fs

from lxman.cli.settings import Dist
from lxman.registry import Lxss

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        ctx.invoke(run)

cli.add_command(config.dist)
cli.add_command(manage.manage)
cli.add_command(fs.fs)

@cli.command("run")
@click.option("--dist", required=False, type=Dist, default=Lxss.default)
@click.option("--elevate", required=False, is_flag=True)
@click.argument('commandline', nargs=-1)
def run(commandline, dist, elevate):
    import shlex
    import subprocess

    lparams = dist.launch_params(commandline)
    if elevate:
        import ctypes
        path, *params = lparams
        params = ' '.join(params)
        ctypes.windll.shell32.ShellExecuteW(None, "runas", path, params, None, 0x00000040)
    else:
        sys.exit(subprocess.call(lparams))

@cli.command("install")
@click.argument("name")
@click.argument("target")
@click.argument("source")
@click.pass_context
def install(ctx, name, target, source):
    import os
    from colorama import Fore
    from lxman.cli.log import Log
    from lxman.registry import Distribution

    log = Log()
    if not os.path.exists(target):
        log.log(Fore.YELLOW + "Creating target directory.")
        os.makedirs(target, exist_ok=True)

    with Distribution.create(name, target) as d:
        log.log(Fore.GREEN + "Distribution created. Guid: " + Fore.CYAN + d.guid)

        log.log(Fore.GREEN + "Creating directory structure")
        ctx.invoke(manage.clean, distribution=d, root=True)

        log.log(Fore.GREEN + "Installing the image")
        ctx.invoke(manage.unpack, distribution=d, source=source)

        log.log(Fore.GREEN + "Fixing missing file-attributes")
        ctx.invoke(fs.fix, path=target)

        return d


@cli.command("clone")
@click.argument("distribution", required=True, type=Dist)
@click.argument("name")
@click.argument("target")
@click.pass_context
def clone(ctx, distribution, name, target):
    from colorama import Fore
    from lxman.cli.log import Log
    from lxman.registry import Distribution
    log = Log()

    d = ctx.invoke(install, name=name, target=target, source=distribution.base_path)
    with d:
        log.log(Fore.GREEN + "Copying Environment-Variables")
        env = d.environment
        env.clear()
        env.update(distribution.environment)
        env.save()

        log.log(Fore.GREEN + "Copying Settings")
        d.default_user = distribution.default_user
        d.cmdline = distribution.cmdline


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


@cli.command("destroy")
@click.argument("distribution", required=True, type=Dist)
@click.option("--yes", is_flag=True, callback=abort_if_false, expose_value=False,
                       prompt="Are you sure to destroy the distribition?")
@click.pass_context
def destroy(ctx, distribution):
    if Lxss.default.guid == distribution.guid:
        print("Cannot destroy default distributions. Switch first.")
        return
    with distribution:
        ctx.invoke(manage.clean, distribution=distribution, root=True)
    distribution.delete()


def main():
    colorama.init()
    cli()
