from colorama import Fore
import click
import sys

from lxman.registry import Lxss
from lxman.cli.page import Page
from lxman.cli.settings import SETTINGS, Dist


@click.group(invoke_without_command=True)
@click.pass_context
def dist(ctx):
    if ctx.invoked_subcommand is None:
        ctx.invoke(list_dists)


@dist.command('show')
@click.argument('name', required=False)
@click.option('--dist', required=False, type=Dist, default=Lxss.default)
@click.option('--raw', is_flag=True)
def show(dist, name, raw):
    pg = Page(dist.name)
    for setting in SETTINGS:
        if name is not None and setting.name != name: continue
        pg.push(setting.name, setting.get(dist))
    pg.output(raw)


@dist.command('config')
@click.option('--dist', type=Dist, default=Lxss.default)
@click.argument('name', required=True)
@click.argument('value', required=True)
def config(dist, name, value):
    for setting in SETTINGS:
        if setting.name != name: continue
        break
    else:
        print(Fore.RED + "Unknown Setting:", Fore.RESET + name)
        sys.exit(2)

    if not setting.set(dist, value):
        print(Fore.RED + "Failed to set:", Fore.RESET + value)
        sys.exit(3)
    else:
        print(Fore.GREEN + "Set:", Fore.RESET + value)

@dist.group(invoke_without_command=True)
@click.pass_context
def env(ctx):
    if ctx.invoked_subcommand is None:
        ctx.invoke(get_env)

@env.command('get')
@click.option("--dist", type=Dist, default=Lxss.default)
@click.option('--raw', is_flag=True)
@click.argument('name', required=False)
def get_env(name, dist, raw):
    pg = Page(dist.name + " > Environment")
    for k, v in dist.environment.items():
        if name is not None and k != name: continue
        pg.push(k, v)
    pg.output(raw)

@env.command('set')
@click.option("--dist", type=Dist, default=Lxss.default)
@click.option('--raw', is_flag=True)
@click.argument('name', required=False)
@click.argument('value', required=False)
def set_env(name, value, dist, raw):
    env = dist.environment
    env[name] = value
    env.save()

@env.command('del')
@click.option("--dist", type=Dist, default=Lxss.default)
@click.option('--raw', is_flag=True)
@click.argument('name', required=False)
def del_env(name, dist, raw):
    env = dist.environment
    del env[name]
    env.save()


@dist.command("list")
@click.option('--raw', is_flag=True)
def list_dists(raw):
    pg = Page('Distributions')
    for distribution in Lxss:
        pg.push(distribution.name, distribution.guid)
    pg.output(raw)
