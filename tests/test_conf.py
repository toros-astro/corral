#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# DOC
# =============================================================================

"""All settings tests"""


# =============================================================================
# IMPORTS
# =============================================================================

import sys

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


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)
