#!/usr/bin/env python
# -*- coding: utf-8 -*-

# License: 3 Clause BSD
# Part of Carpyncho - http://carpyncho.jbcabral.org


# =============================================================================
# DOCS
# =============================================================================

"""This file is for distribute corral

"""


# =============================================================================
# IMPORTS
# =============================================================================

import sys

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

import corral


# =============================================================================
# CONSTANTS
# =============================================================================

REQUIREMENTS = [
    "SQLAlchemy>=1.0.8",
    "SQLAlchemy-Utils>=0.31.0",
    "six>=1.10.0",
    "texttable>=0.8.3"
]


# =============================================================================
# FUNCTIONS
# =============================================================================

def do_setup():
    setup(
        name=corral.NAME,
        version=corral.VERSION,
        description=corral.DOC,
        author=corral.AUTHORS,
        author_email=corral.EMAIL,
        url=corral.URL,
        license=corral.LICENSE,
        keywords=corral.KEYWORDS,
        classifiers=(
            "Development Status :: 4 - Beta",
            "Intended Audience :: Education",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: BSD License",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.4",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: Implementation :: CPython",
            "Topic :: Scientific/Engineering",
        ),
        packages=[pkg for pkg in find_packages() if pkg.startswith("corral")],
        py_modules=["ez_setup"],
        install_requires=REQUIREMENTS,
        entry_points={
            'console_scripts': [
                'corral = corral.noenvcli:run_from_command_line']}
    )


def do_publish():
    pass

if __name__ == "__main__":
    if sys.argv[-1] == 'publish':
        do_publish()
    else:
        do_setup()
