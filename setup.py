#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='bfh',
    version="0.1.0",
    description="Smacks schemas into other schemas",
    author="Evan Bender",
    install_requires=[
        "python-dateutil",
    ],
    author_email="maccruiskeen@gmail.com",
    url="https://github.com/benauthor/bfh",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
    ],
    packages=["bfh"],
)
