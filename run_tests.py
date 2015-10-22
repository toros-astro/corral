#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse


DEFAULT_SETTINGS = "toritos.settings"


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


if __name__ == "__main__":
    parser = create_parser()
    arguments = parser.parse_args(sys.argv[1:])

    os.environ.setdefault("CORRAL_SETTINGS_MODULE", arguments.settings)

    from corral import tests
    result = tests.run_tests(
        verbosity=arguments.verbosity, failfast=arguments.failfast)
    sys.exit(not result.wasSuccessful())

