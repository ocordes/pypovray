"""

written by: Oliver Cordes 2019-04-08
changed by: Oliver Cordes 2019-04-08
"""

import click

import sys


@click.group()
#@click.argument('--script', envvar='PYPOV_APP')
#@click.option('--script', envvar='PYPOV_APP')
def cli():
    """pypov program loader"""
    #click.echo('Hello World2!')
    #click.echo(script)


@cli.command()
@click.argument('pyscript', envvar='PYPOV_APP')
def run(pyscript):
    """Runs a pypov script """
    click.echo('run')
    click.echo(pyscript)
