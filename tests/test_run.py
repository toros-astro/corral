#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# DOC
# =============================================================================

"""All Corral base tests"""


# =============================================================================
# IMPORTS
# =============================================================================

from corral import run, conf, exceptions

import mock

from .steps import TestLoader

from .base import BaseTest


# =============================================================================
# BASE CLASS
# =============================================================================

class TestSteps(BaseTest):

    def test_load_loader(self):
        actual = run.load_loader()
        self.assertIs(actual, TestLoader)

        with mock.patch("corral.conf.settings.LOADER", new="os.open"):
            with self.assertRaises(exceptions.ImproperlyConfigured):
                run.load_loader()


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)
