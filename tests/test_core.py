#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# DOC
# =============================================================================

"""All settings tests"""


# =============================================================================
# IMPORTS
# =============================================================================

from corral import core, VERSION

import mock

from .base import BaseTest


# =============================================================================
# BASE CLASS
# =============================================================================

class TestCore(BaseTest):

    def test_get_version(self):
        actual = core.get_version()
        expected = VERSION
        self.assertEqual(actual, expected)

    def test_setup_environment(self):
        with mock.patch("corral.db.setup") as setup:
            with mock.patch("corral.db.load_models_module") as load_mm:
                core.setup_environment()
                self.assertTrue(setup.called)
                self.assertTrue(load_mm.called)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)
