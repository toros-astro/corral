#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# IMPORTS
# =============================================================================

import sys

import six

from . import util, creator


# =============================================================================
# CONSTANTS
# =============================================================================

def create_parser():
    parser = util.CorralCLIParser()

    # creator parser
    subparser = parser.add_subparser(
        "create", creator.create_pipeline,
        description="Create a fresh pipeline")
    subparser.add_argument("path", action="store", help="New Pipeline Path")

    # returning
    return parser


def run_from_command_line():
    parser = create_parser()
    func, kwargs, gkwargs = parser.parse_args(sys.argv[1:])
    try:
        func(**kwargs)
    except BaseException as err:
        sys.stderr.write("{}\n".format(err))
        if gkwargs.get("stacktrace"):
            six.reraise(type(err), err, six.sys.exc_traceback)
