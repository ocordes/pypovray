# -*- coding: utf-8 -*-
"""

written by: Oliver Cordes 2019-04-08
changed by: Oliver Cordes 2019-05-04
"""

import click

import os, sys
import traceback
import importlib


from pypovlib.pypovapp import PovApp


# some exceptions
class NoAppException(click.UsageError):
    """Raised if an application cannot be found or loaded."""


def prepare_import(path):
    """Given a filename this will try to calculate the python path, add it
    to the search path and return the actual module name that is expected.
    """
    path = os.path.realpath(path)

    if os.path.splitext(path)[1] == '.py':
        path = os.path.splitext(path)[0]

    if os.path.basename(path) == '__init__':
        path = os.path.dirname(path)

    module_name = []

    # move up until outside package structure (no __init__.py)
    while True:
        path, name = os.path.split(path)
        module_name.append(name)

        if not os.path.exists(os.path.join(path, '__init__.py')):
            break

    if sys.path[0] != path:
        sys.path.insert(0, path)

    return '.'.join(module_name[::-1])


def import_script(module_name, raise_if_not_found=True):
    __traceback_hide__ = True

    try:
        #__import__(module_name)
        module = importlib.import_module(module_name)
    except ImportError:
        # Reraise the ImportError if it occurred within the imported module.
        # Determine this by checking whether the trace has a depth > 1.
        if sys.exc_info()[-1].tb_next:
            raise NoAppException(
                'While importing "{name}", an ImportError was raised:'
                '\n\n{tb}'.format(name=module_name, tb=traceback.format_exc())
            )
        elif raise_if_not_found:
            raise NoAppException(
                'Could not import "{name}".'.format(name=module_name)
            )
        else:
            return None

    return module


def locate_app(module):
    app = None

    # Search for the most common names first.
    for attr_name in ('app', 'application'):
        app = getattr(module, attr_name, None)

        if isinstance(app, PovApp):
            return app

    return app


def load_app(script):
    # update names and path for module loading
    import_name = prepare_import(script)
    module = import_script(import_name)
    if module is None:
        raise NoAppException(
            'Module is none.'
        )

    app = locate_app(module)

    return app



@click.group()
#@click.argument('--script', envvar='PYPOV_APP')
#@click.option('--script', envvar='PYPOV_APP')
def cli():
    """pypov program loader"""
    #click.echo('Hello World2!')
    #click.echo(script)


@cli.command()
@click.argument('pyscript', envvar='PYPOV_APP')
@click.option('--fps', type=int, help='fps for the animation')
@click.option('--frames', type=int, help='numer of animation frames')
@click.option('--duration', type=int, help='duration of the animation in seconds')
def build(pyscript, fps, frames, duration):
    """Run the build process from a pypov script """
    app = load_app(pyscript)
    if app is None:
        click.echo('PovFile application not found!')
    else:
        click.echo('PovFile application found ...')

    # set all parameters individually
    app.set_fps(fps)
    app.set_frames(frames)
    app.set_duration(duration)

    # build
    app.build()


@cli.command()
@click.argument('pyscript', envvar='PYPOV_APP')
@click.option('--width', type=int, help='width of the render image')
@click.option('--height', type=int, help='height of the render image')
@click.option('--fps', type=int, help='fps for the animation')
@click.option('--frames', type=int, help='numer of animation frames')
@click.option('--duration', type=int, help='duration of the animation in seconds')
def create(pyscript, width, height, fps, frames, duration):
    """Runs a pypov script without the RQ submission"""
    app = load_app(pyscript)
    if app is None:
        click.echo('PovFile application not found!')
    else:
        click.echo('PovFile application found ...')

    # set all parameters individually
    app.set_geometry(width,height)
    app.set_fps(fps)
    app.set_frames(frames)
    app.set_duration(duration)

    # build and run
    app.build()
    app.create()


@cli.command()
@click.argument('pyscript', envvar='PYPOV_APP')
@click.option('--project', type=str, default='', help='project name or id')
@click.option('--width', type=int, help='width of the render image')
@click.option('--height', type=int, help='height of the render image')
@click.option('--fps', type=int, help='fps for the animation')
@click.option('--frames', type=int, help='numer of animation frames')
@click.option('--duration', type=int, help='duration of the animation in seconds')
def run(pyscript, width, height, fps, frames, duration, project):
    """Runs a pypov script """
    app = load_app(pyscript)
    if app is None:
        click.echo('PovFile application not found!')
    else:
        click.echo('PovFile application found ...')

    # set all parameters individually
    app.set_geometry(width,height)
    app.set_fps(fps)
    app.set_frames(frames)
    app.set_duration(duration)
    app.set_project(project)

    # build and run
    app.build()
    app.run()


if __name__ == '__main__':
    cli()
