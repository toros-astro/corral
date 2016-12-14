#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# IMPORT
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
