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
import inspect

from .base import BaseTest

from corral import core, VERSION

from . import models


# =============================================================================
# BASE CLASS
# =============================================================================

class TestCore(BaseTest):

    def test_get_version(self):
        actual = core.get_version()
        expected = ".".join(VERSION)
        self.assertEqual(actual, expected)

    def test_setup_environment(self):
        # if this not work all the tests must fails so... nothing
        pass




# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)
