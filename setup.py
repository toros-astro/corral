#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016-2017, Cabral, Juan; Sanchez, Bruno & Berois, Martín
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# * Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.

# * Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

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

import setuptools

import corral


# =============================================================================
# CONSTANTS
# =============================================================================

REQUIREMENTS = [
    'alembic>=0.8.4',
    'attrs>=16.2.0',
    'coverage>=4.0.3',
    'flake8<3.0.0',
    'Jinja2>=2.8',
    'mock>=1.3.0',
    'sadisplay>=0.4.6',
    'sh>=1.11',
    'six>=1.10.0',
    'SQLAlchemy>=1.0.8',
    'SQLAlchemy-Utils>=0.31.0',
    'termcolor>=1.1.0',
    'texttable>=0.8.3',
    'xmltodict>=0.10.1'
]

with open('README.rst') as fp:
    LONG_DESCRIPTION = fp.read()


# =============================================================================
# FUNCTIONS
# =============================================================================

def do_setup():
    setuptools.setup(
        name=corral.NAME,
        version=corral.VERSION,
        description=corral.DOC,
        long_description=LONG_DESCRIPTION,
        author=corral.AUTHORS,
        author_email=corral.EMAIL,
        url=corral.URL,
        license=corral.LICENSE,
        keywords=corral.KEYWORDS,
        classifiers=(
            "Development Status :: 4 - Beta",
            'Intended Audience :: Science/Research',
            'Intended Audience :: Developers',
            'License :: OSI Approved',
            'Operating System :: POSIX',
            'Operating System :: Unix',
            'Operating System :: MacOS',
            "Programming Language :: Python",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.4",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: Implementation :: CPython",
            "Topic :: Scientific/Engineering",
            'Topic :: Software Development'
        ),
        packages=[
            pkg for pkg in setuptools.find_packages()
            if pkg.startswith("corral")],
        py_modules=["ez_setup"],
        install_requires=REQUIREMENTS,
        include_package_data=True,
        entry_points={
            'console_scripts': [
                'corral = corral.cli:run_from_command_line']}
    )


def do_publish():
    pass

if __name__ == "__main__":
    if sys.argv[-1] == 'publish':
        do_publish()
    else:
        do_setup()
