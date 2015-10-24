#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import types
import unittest
import glob
import importlib
import logging

import six


# =============================================================================
# CONSTANTS
# =============================================================================

DEFAULT_SETTINGS = "tests.settings"

PATH = os.path.abspath(os.path.dirname(__file__))

TESTS_PATH = os.path.join(PATH, "tests")

GLOB_FILTER = os.path.join(TESTS_PATH, "*.py")

TEST_MODULES = [
    os.path.splitext(os.path.basename(fn))[0]
    for fn in glob.glob(GLOB_FILTER)
    if os.path.basename(fn).startswith("test_")]


# =============================================================================
# LOGGING
# =============================================================================

logging.basicConfig(format="[%(asctime)-15s] %(message)s'")
logger = logging.getLogger("CorralTest")


# =============================================================================
# FUNCTIONS
# =============================================================================

def create_parser():
    parser = argparse.ArgumentParser(
        description="Run the core test cases for Corral")
    parser.add_argument(
        "-v", "--verbose", dest='verbosity',  default=1, const=2,
        help='Verbose output', action='store_const')
    parser.add_argument(
        "-f", "--failfast", dest='failfast', default=False,
        help='Stop on first fail or error', action='store_true')
    parser.add_argument(
        "--settings", dest='settings', default=DEFAULT_SETTINGS,
        help='Settings to run the test cases', action='store')

    return parser


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
            logger.error(six.text_type(err))
    return runner.run(suite)


def main(argv):
    parser = create_parser()
    arguments = parser.parse_args(argv)

    os.environ.setdefault("CORRAL_SETTINGS_MODULE", arguments.settings)

    from corral import core, conf, db

    # SETUP THE ENVIRONMENT
    core.setup_environment()
    db.create_all()

    # RUN THE TESTS
    result = run_tests(
        verbosity=arguments.verbosity, failfast=arguments.failfast)

    # EXIT WITH CORRECT STATUS
    sys.exit(not result.wasSuccessful())


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    main(sys.argv[1:])

