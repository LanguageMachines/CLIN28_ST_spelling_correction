#! /usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import print_function

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "clin28tools",
    version = "0.1.1",
    author = "Maarten van Gompel, Merijn Beeksma, Florian Kunneman",
    author_email = "proycon@anaproy.nl",
    description = ("Scripts for the CLIN28 Shared Task on spelling correction"),
    license = "GPL",
    keywords = "nlp computational_linguistics spelling_correction",
    url = "https://github.com/LanguageMachines/CLIN28_ST_spelling_correction",
    packages=['clin28tools'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Text Processing :: Linguistic",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Operating System :: POSIX",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    zip_safe=False,
    include_package_data=True,
    package_data = { },
    install_requires=[ 'pynlpl'],
    entry_points = {    'console_scripts': [
        'clin28-validator = clin28tools.validator:main' ,
        'clin28-folia2json = clin28tools.folia2json:main' ,
        'clin28-evaluate = clin28tools.evaluate:main' ,
    ] }
)
