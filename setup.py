#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='mse-parse',
    version="0.1",
    author='Steve Yeago',
    author_email='subsume@gmail.com',
    description='Python parser for Magic Set Editor (MSE) files',
    url='http://github.com/subsume/mse-parser',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],
)
