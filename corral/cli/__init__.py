#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import copy
import argparse

import six

from .. import core, conf, util, exceptions
from .base import BaseCommand


# =============================================================================
# CONSTANTS
# =============================================================================

COMMANDS_MODULE = "{}.commands".format(conf.PACKAGE)

MODE_IN, MODE_TEST, MODE_OUT = "in", "test", "out"


# =============================================================================
# CLASS
# =============================================================================

class CorralCLIParser(object):

    def __init__(self, description):
        self.global_parser = argparse.ArgumentParser(description=description)
        self.global_parser.add_argument(
            "--version", "-v", action="version", version=core.get_version())
        self.global_parser.add_argument(
            "-x", "--stacktrace", dest="stacktrace",
            action="store_true", default=False)

        cmd_help = (
            "For more information please run 'python {} <COMMAND> --help'"
        ).format(sys.argv[0])
        self.subparsers = self.global_parser.add_subparsers(help=cmd_help)

    def add_subparser(self, title, command, mode, **kwargs):
        if mode not in (MODE_IN, MODE_OUT, MODE_TEST):
            msg = "Command mode must be '{}', '{}', or '{}'. Found '{}'"
            raise ValueError(MODE_IN, MODE_OUT, MODE_TEST, msg.format(mode))
        parser = self.subparsers.add_parser(title, **kwargs)
        parser.set_defaults(command=command)
        parser.set_defaults(mode=mode)
        return parser

    def extract_func(self, ns):
        kwargs = dict(ns._get_kwargs())
        command = kwargs.pop("command")
        mode = kwargs.pop("mode")
        func_kwargs, global_kwargs = {}, {}
        for k, v in kwargs.items():
            if k in ("stacktrace",):
                global_kwargs[k] = v
            else:
                func_kwargs[k] = v
        return command, mode, func_kwargs, global_kwargs

    def parse_args(self, argv):
        parsed_args = self.global_parser.parse_args(argv)
        return self.extract_func(parsed_args)


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

    description = core.get_description()
    parser = CorralCLIParser(description)

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
    if mode == MODE_IN:
        core.setup_environment()
    elif mode == MODE_TEST:
        core.setup_environment(test_mode=True)
    try:
        command.handle(**kwargs)
    except BaseException as err:
        sys.stderr.write("{}\n".format(err))
        if gkwargs.get("stacktrace"):
            six.reraise(type(err), err, six.sys.exc_traceback)
