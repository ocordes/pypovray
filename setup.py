from setuptools import setup


from pypovlib.pypovobjects import __version__, __author__

setup(
    name='pypovlib',
    version=__version__,
    author=__author__,
    py_modules=['pypov'],
    packages=['pypovlib'],
    install_requires=[
     'numpy',
     'Click',
    ],
    entry_points='''
        [console_scripts]
        pypov=pypov:cli
    ''',
)
