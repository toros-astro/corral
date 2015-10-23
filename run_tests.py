#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import types

PKG_NAME = "test"

DEFAULT_SETTINGS = "{}.virtual_settings".format(PKG_NAME)

DEFAULT_MODELS = "{}.models".format(PKG_NAME)

TEST_NS = {
    "DEBUG": True,
    "CONNECTION": 'sqlite:///:memory:'
}


def default_settings_module_name():
    settings = types.ModuleType(DEFAULT_SETTINGS)
    sys.modules[DEFAULT_SETTINGS] = settings

    models = types.ModuleType(DEFAULT_MODELS)
    sys.modules[DEFAULT_MODELS] = models

    return DEFAULT_SETTINGS


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
        "--settings", dest='settings', default=None,
        help='Settings to run the test cases', action='store')

    return parser


if __name__ == "__main__":
    parser = create_parser()
    arguments = parser.parse_args(sys.argv[1:])

    settings = arguments.settings or default_settings_module_name()

    os.environ.setdefault("CORRAL_SETTINGS_MODULE", settings)

    from corral import core, conf, tests, db

    # SETUP THE ENVIRONMENT
    conf.settings.update(TEST_NS)
    core.setup_environment()
    db.create_all()

    # RUN THE TESTS
    result = tests.run_tests(
        verbosity=arguments.verbosity, failfast=arguments.failfast)

    # EXIT WITH CORRECT STATUS
    sys.exit(not result.wasSuccessful())

