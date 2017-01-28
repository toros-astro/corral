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
# IMPORTS
# =============================================================================

import collections
import importlib


# =============================================================================
# CLASS
# =============================================================================

class LazyImport(object):

    def __init__(self, importpath):
        self._importpath = importpath
        self._object = None

    def __repr__(self):
        return "<LazyImport '{}'>".format(self._importpath)

    def resolve(self):
        importpath = self._importpath
        if "." in importpath:
            module_name, cls_name = importpath.rsplit(".", 1)
            try:
                module = importlib.import_module(module_name)
                return getattr(module, cls_name)
            except (ImportError, AttributeError):
                pass
        return importlib.import_module(importpath)

        return self._object

    def __getattr__(self, name):
        if self._object is None:
            self._object = self.resolve()
        return getattr(self._object, name)


# =============================================================================
# FUNCTIONS
# =============================================================================

def to_namedtuple(name, d):
    keys = list(d.keys())
    namedtuple = collections.namedtuple(name, keys)
    return namedtuple(**d)


def collect_subclasses(cls):
    def collect(basecls):
        collected = set()
        for subcls in basecls.__subclasses__():
            collected.add(subcls)
            collected.update(collect(subcls))
        return collected
    return tuple(collect(cls))


def dimport(importpath, lazy=False):
    lazy_import = LazyImport(importpath)
    return lazy_import if lazy else lazy_import.resolve()
