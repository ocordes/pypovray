#!/bin/sh

pip uninstall pypovlib
rm -rf pypovlib.egg-info/
pip install --editable .
