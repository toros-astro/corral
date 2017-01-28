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
