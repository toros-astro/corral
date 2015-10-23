#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# IMPORT
# =============================================================================

import os
import importlib

from . import util


# =============================================================================
# CONSTANTS
# =============================================================================

CORRAL_SETTINGS_MODULE = os.environ["CORRAL_SETTINGS_MODULE"]

PACKAGE = CORRAL_SETTINGS_MODULE.split(".", 1)[0]

DEFAULT_SETTINGS = util.to_namedtuple(
    'DefaultSettings', {
        "DEBUG": True,
        "CONNECTION": 'sqlite:///corral-dev.db'})


# =============================================================================
# CLASS
# =============================================================================

class LazySettings(object):

    def __init__(self, settings_module_name):
        self._settings_module_name = settings_module_name
        self._settings = importlib.import_module(settings_module_name)

    def update(self, ns):
        self.__dict__.update(ns)

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError("'{}' is a private setting name".format(name))
        try:
            return getattr(self._settings, name)
        except AttributeError:
            try:
                return getattr(DEFAULT_SETTINGS, name)
            except AttributeError:
                raise AttributeError("Setting '{}' not found".format(name))

    def __repr__(self):
        return "<LazySettings '{}'>".format(self._settings_module_name)

    def __str__(self):
        return repr(self)


# =============================================================================
# LOAD
# =============================================================================

settings = LazySettings(CORRAL_SETTINGS_MODULE)
