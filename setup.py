#!/usr/bin/env python
try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(
    name='django-ztask',
    packages=['django_ztask'],
    install_requires=[
        'pyzmq',
    ]
)
