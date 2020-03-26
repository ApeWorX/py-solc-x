#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

setup(
    name="py-solc-x",
    version="0.8.1",
    description="""Python wrapper around the solc binary with 0.5.x and 0.6.x support""",
    long_description_markdown_filename="README.md",
    author="Ben Hauser (forked from py-solc by Piper Merriam)",
    author_email="ben@hauser.id",
    url="https://github.com/iamdefinitelyahuman/py-solc-x",
    include_package_data=True,
    py_modules=["solcx"],
    setup_requires=["setuptools-markdown"],
    python_requires=">=3.4, <4",
    install_requires=["semantic_version>=2.8.1,<3", "requests>=2.19.0,<3"],
    license="MIT",
    zip_safe=False,
    keywords="ethereum solidity solc",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
