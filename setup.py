#!/usr/bin/env python
try:
    from setuptools import setup, find_packages
except:
    from distutils.core import setup
import django_ztask as distmeta

setup(
    version=distmeta.__version__,
    description=distmeta.__doc__,
    author=distmeta.__author__,
    author_email=distmeta.__contact__,
    url=distmeta.__homepage__,
    #
    name='django-ztask',
    packages=find_packages(),
    install_requires=[
        'pyzmq',
    ]
)
