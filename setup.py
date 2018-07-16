#!/usr/bin/env python

import os.path

from setuptools import setup


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name="dbupgrade",
    version="1.0.0",
    description="Database Migration Tool",
    long_description=read("README.rst"),
    author="Sebastian Rittau",
    author_email="srittau@rittau.biz",
    url="https://github.com/srittau/dbupgrade",
    packages=["dbupgrade"],
    scripts=[os.path.join("bin", "dbupgrade")],
    python_requires=">= 3.5, < 3.8",
    install_requires=["sqlalchemy >= 1.0"],
    tests_require=[
        "asserts >= 0.8.1, < 0.9",
        "dectest >= 0.1.2, < 0.2",
    ],
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Database",
        "Topic :: Software Development",
    ],
)
