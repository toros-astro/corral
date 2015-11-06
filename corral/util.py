#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# IMPORT
# =============================================================================

import collections
import importlib
import argparse

from . import core


# =============================================================================
# CLASS
# =============================================================================

class CorralCLIParser(object):

    def __init__(self):
        self.global_parser = argparse.ArgumentParser(
            description=core.get_description())
        self.global_parser.add_argument(
            "--version", action="version", version=core.get_version())
        self.subparsers = self.global_parser.add_subparsers(
            help="command help")

    def add_subparser(self, title, func, **kwargs):
        parser = self.subparsers.add_parser(title, **kwargs)
        parser.set_defaults(func=func)
        return parser

    def extract_func(self, ns):
        kwargs = dict(ns._get_kwargs())
        func = kwargs.pop("func")
        return func, kwargs

    def parse_args(self, argv):
        parsed_args = self.global_parser.parse_args(argv)
        return self.extract_func(parsed_args)


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


def dimport(importpath):
    if "." in importpath:
        module_name, cls_name = importpath.rsplit(".", 1)
        try:
            module = importlib.import_module(module_name)
            return getattr(module, cls_name)
        except (ImportError, AttributeError):
            pass
    return importlib.import_module(importpath)
