#!/usr/bin/env python3

import os.path

from setuptools import setup


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name="dbupgrade",
    version="2.1.0",
    description="Database Migration Tool",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="Sebastian Rittau",
    author_email="srittau@rittau.biz",
    url="https://github.com/srittau/dbupgrade",
    packages=["dbupgrade"],
    scripts=[os.path.join("bin", "dbupgrade")],
    python_requires=">= 3.7",
    install_requires=["sqlalchemy >= 1.4", "sqlparse >= 0.3.0"],
    tests_require=["asserts >= 0.8.1, < 0.12", "dectest >= 1.0.0, < 2"],
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
