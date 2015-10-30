#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# IMPORT
# =============================================================================

import collections
import importlib


# =============================================================================
# FUNCTIONS
# =============================================================================

def to_namedtuple(name, d):
    keys = list(d.keys())
    namedtuple = collections.namedtuple(name, d)
    return namedtuple(**d)


def collect_subclasses(cls):
    def collect(basecls):
        collected = set()
        for subcls in basecls.__subclasses__():
            collected.add(subcls)
            collected.update(collect(subcls))
        return collected
    return tuple(collect(cls))


def dimport(importpath):
    if "." in importpath:
        module_name, cls_name = importpath.rsplit(".", 1)
        try:
            module = importlib.import_module(module_name)
            return getattr(module, cls_name)
        except (ImportError, AttributeError):
            pass
    try:
        return importlib.import_module(importpath)
    except:
        raise ImportError("No module named {}".format(importpath))
