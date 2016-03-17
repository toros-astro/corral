#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import copy

import six

from .. import core, conf, util, exceptions
from .base import BaseCommand


# =============================================================================
# CONSTANTS
# =============================================================================

COMMANDS_MODULE = "{}.commands".format(conf.PACKAGE)


# =============================================================================
# FUNCTIONS
# =============================================================================

def load_commands_module():
    if conf.settings.has_module("commands"):
        try:
            return util.dimport(COMMANDS_MODULE)
        except ImportError as err:
            core.logger.info(six.text_type(err))


def create_parser():

    from . import commands  # noqa

    load_commands_module()

    command_names = set()

    parser = util.CorralCLIParser()

    for cls in util.collect_subclasses(BaseCommand):

        options = copy.deepcopy(cls.get_options())

        title = options.pop("title", cls.__name__.lower())
        mode = options.pop("mode", "in")
        options["description"] = options.get("description", cls.__doc__) or ""

        if title in command_names:
            msg = "Duplicate Command '{}'".format(title)
            raise exceptions.ImproperlyConfigured(msg)
        command_names.add(title)

        command = cls()
        sub_parser = parser.add_subparser(title, command, mode, **options)
        command.configure(sub_parser)
        command.setup()

    return parser


def run_from_command_line():
    parser = create_parser()
    command, mode, kwargs, gkwargs = parser.parse_args(sys.argv[1:])
    if mode == "in":
        core.setup_environment()
    elif mode == "test":
        core.setup_environment(test_mode=True)
    try:
        command.handle(**kwargs)
    except BaseException as err:
        sys.stderr.write("{}\n".format(err))
        if gkwargs.get("stacktrace"):
            six.reraise(type(err), err, six.sys.exc_traceback)
