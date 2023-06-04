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
import sys
import argparse
import unittest
import glob
import importlib
import logging
import atexit

from corral import util

from tests import base


# =============================================================================
# CONSTANTS
# =============================================================================

DEFAULT_SETTINGS = "tests.settings"

PATH = os.path.abspath(os.path.dirname(__file__))

TESTS_PATH = os.path.join(PATH, "tests")

GLOB_FILTER = os.path.join(TESTS_PATH, "*.py")

VERSIONS_PATH = os.path.join(TESTS_PATH, "migrations", "versions")

VERSIONS_GLOB = os.path.join(VERSIONS_PATH, "*.py")


# =============================================================================
# LOGGING
# =============================================================================

logging.basicConfig(format="[%(asctime)-15s] %(message)s'")
logger = logging.getLogger("CorralTest")


# =============================================================================
# FUNCTIONS
# =============================================================================

def delete_versions():
    for file_path in glob.glob(VERSIONS_GLOB):
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


def create_parser():
    parser = argparse.ArgumentParser(
        description="Run the core test cases for Corral")

    parser.add_argument(
        "-f", "--failfast", dest='failfast', default=False,
        help='Stop on first fail or error', action='store_true')
    parser.add_argument(
        "--settings", dest='settings', default=DEFAULT_SETTINGS,
        help='Settings to run the test cases', action='store')

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "-v", "--verbose", dest='verbosity',  default=1, const=2,
        help='Verbose output', action='store_const')
    group.add_argument(
        "-vv", "--vverbose", dest='verbosity', const=3,
        help='Verbose output', action='store_const')

    return parser


def load_test_modules():
    test_modules_names = [
        os.path.splitext(os.path.basename(fn))[0]
        for fn in glob.glob(GLOB_FILTER)
        if os.path.basename(fn).startswith("test_")]
    test_modules = set()
    for modname in test_modules_names:
        dot_modname = ".{}".format(modname)
        module = importlib.import_module(dot_modname, "tests")
        test_modules.add(module)
    return tuple(test_modules)


def run_tests(verbosity=1, failfast=False):
    """Run test of corral"""

    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    runner = unittest.runner.TextTestRunner(
        verbosity=verbosity, failfast=failfast)

    load_test_modules()

    for testcase in util.collect_subclasses(base.BaseTest):
        tests = loader.loadTestsFromTestCase(testcase)
        if tests.countTestCases():
            suite.addTests(tests)
    return runner.run(suite)


def main(argv):
    parser = create_parser()
    arguments = parser.parse_args(argv)

    os.environ.setdefault("CORRAL_SETTINGS_MODULE", arguments.settings)

    from corral import core, conf, db

    # SETUP THE ENVIRONMENT
    if arguments.verbosity < 3:
        conf.settings.DEBUG = False
    core.setup_environment()
    db.create_all()
    core.logger.setLevel(core.logging.CRITICAL)
    atexit.register(delete_versions)

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
