#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# IMPORT
# =============================================================================

import os
import logging

from . import util


# =============================================================================
# CONSTANTS
# =============================================================================

CORRAL_SETTINGS_MODULE = os.environ["CORRAL_SETTINGS_MODULE"]

PACKAGE = CORRAL_SETTINGS_MODULE.rsplit(".", 1)[0]

DEFAULT_SETTINGS = util.to_namedtuple(
    'DefaultSettings', {
        "LOG_LEVEL": logging.INFO,
        "LOG_FORMAT": '[%(levelname)s] %(message)s'})


# =============================================================================
# CLASS
# =============================================================================

class LazySettings(object):

    def __init__(self, settings_module_name):
        self._settings_module_name = settings_module_name
        self._settings = util.dimport(settings_module_name)
        self._path = os.path.dirname(self._settings.__file__)

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

    def get_settings_module(self):
        return self._settings

    def has_module(self, name):
        name = name.rsplit(".", 1)[-1]
        full_path = os.path.join(self._path, name)
        return (
            os.path.isfile(full_path + ".py") or
            os.path.isfile(full_path + ".pyc"))

    def get(self, name, d=None):
        return getattr(self._settings, name, d)


# =============================================================================
# LOAD
# =============================================================================

settings = LazySettings(CORRAL_SETTINGS_MODULE)
