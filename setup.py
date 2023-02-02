#!/usr/bin/env python
from setuptools import find_packages
from setuptools import setup

setup(
    name='mars_parse',
    version='0.1.0',
    author='Jacob Medeiros',
    author_email='jacobmedeiros16@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=['typer','rich'],
    license = 'MIT',
)