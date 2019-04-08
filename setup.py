from setuptools import setup

setup(
    name='pypovlib',
    version='0.0.1',
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
