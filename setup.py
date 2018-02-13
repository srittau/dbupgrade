#!/usr/bin/env python

from setuptools import setup


setup(
    name="dbupgrade",
    version="0.1.0",
    description="Database Upgrading Framework",
    author="Sebastian Rittau",
    author_email="srittau@rittau.biz",
    url="https://github.com/srittau/dbupgrade",
    packages=["dbupgrade"],
    scripts=["bin/dbupgrade"],
    install_requires=["sqlalchemy>=1.0"],
    tests_require=["asserts>=0.8.1,<0.9"],
)
