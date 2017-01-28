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
# DOC
# =============================================================================

"""All pipeline configurations tests"""


# =============================================================================
# IMPORTS
# =============================================================================

import sys
import string
import random

from corral import conf

from .base import BaseTest


# =============================================================================
# BASE CLASS
# =============================================================================

class TestLazySettings(BaseTest):

    def setup(self):
        self.module_name = conf.CORRAL_SETTINGS_MODULE
        self.lazy_settings = conf.LazySettings(conf.CORRAL_SETTINGS_MODULE)
        self.settings = sys.modules[conf.CORRAL_SETTINGS_MODULE]

    def test_same_module(self):
        self.assertEqual(
            self.lazy_settings.get_settings_module(), self.settings)

    def test_set_new_setting(self):
        original = self.lazy_settings.CONNECTION
        try:
            self.lazy_settings.CONNECTION = ""
            self.assertEqual(self.lazy_settings.CONNECTION, "")
            self.assertNotEqual(
                self.lazy_settings.CONNECTION,
                getattr(self.settings, "CONNECTION", "Nope"))
        finally:
            self.lazy_settings.CONNECTION = original
        self.assertEqual(self.lazy_settings.CONNECTION, original)

    def test_set_update(self):
        original = self.lazy_settings.CONNECTION
        try:
            ns = {"CONNECTION": ""}
            self.lazy_settings.update(ns)
            self.assertEqual(self.lazy_settings.CONNECTION, "")
            self.assertNotEqual(
                self.lazy_settings.CONNECTION,
                getattr(self.settings, "CONNECTION", "Nope"))
        finally:
            self.lazy_settings.CONNECTION = original
        self.assertEqual(self.lazy_settings.CONNECTION, original)

    def test_has_module(self):
        self.assertTrue(self.lazy_settings.has_module("models"))
        self.assertFalse(self.lazy_settings.has_module("___models___"))

    def test_private_name(self):
        with self.assertRaises(AttributeError):
            self.lazy_settings._a

    def test_invalid_name(self):
        with self.assertRaises(AttributeError):
            self.lazy_settings.foxyroxy

    def test_str_repr(self):
        self.assertEqual(repr(self.lazy_settings), str(self.lazy_settings))

    def test_get(self):
        self.assertEqual(
            self.lazy_settings.get("CONNECTION", "x"),
            self.settings.CONNECTION)

        letters = list(string.digits + string.ascii_letters)
        random.shuffle(letters)
        non_existing_attr = "attr_" + str(letters[:5])
        while hasattr(self.settings, non_existing_attr):
            random.shuffle(letters)
            non_existing_attr += str(letters[:2])

        self.assertEqual(self.lazy_settings.get(non_existing_attr, "x"), "x")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)
