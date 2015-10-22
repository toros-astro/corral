#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# FUTURE
# =============================================================================




# =============================================================================
# DOC
# =============================================================================

__doc__ = """All coral tests"""


# =============================================================================
# IMPORTS
# =============================================================================

import os
import unittest
import glob
import importlib
import argparse

import six

from .. import core, util
from . import base


# =============================================================================
# CONSTANTS
# =============================================================================

PATH = os.path.abspath(os.path.dirname(__file__))

GLOB_FILTER = os.path.join(PATH, "*.py")

TEST_MODULES = [
    os.path.splitext(os.path.basename(fn))[0]
    for fn in glob.glob(GLOB_FILTER)
    if os.path.basename(fn).startswith("test_")]


# =============================================================================
# FUNCTIONS
# =============================================================================

def run_tests(verbosity=1, failfast=False):
    """Run test of corral"""

    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    runner = unittest.runner.TextTestRunner(
        verbosity=verbosity, failfast=failfast)

    for modname in TEST_MODULES:
        try:
            dot_modname = ".{}".format(modname)
            module = importlib.import_module(
                dot_modname, package="corral.tests")
            tests = loader.loadTestsFromModule(module)
            if tests.countTestCases():
                    suite.addTests(tests)
        except ImportError as err:
            core.logger.error(six.text_type(err))
    return runner.run(suite)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)
