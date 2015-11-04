#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

import six

from .. import core, conf, util
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
            core.logger.error(six.text_type(err))

def create_parser():

    from . import commands  # noqa

    load_commands_module()

    command_names = set()

    global_parser = argparse.ArgumentParser(
        description="Powerful pipeline framework", version=core.get_version())
    subparsers = global_parser.add_subparsers(help="command help")

    for cls in util.collect_subclasses(BaseCommand):
        options = getattr(cls, "options", {}) or {}
        title = options.pop("title", cls.__name__.lower())
        options["description"] = options.get("description", cls.__doc__) or ""

        if title in command_names:
            raise ValueError("Duplicate Command '{}'".format(title))
        command_names.add(title)

        parser = subparsers.add_parser(title, **options)
        command = cls(parser)
        command.setup()
        parser.set_defaults(func=command.handle)

    return global_parser


def extract_func(ns):
    kwargs = dict(ns._get_kwargs())
    func = kwargs.pop("func")
    return func, kwargs


def run_from_command_line(args):
    core.setup_environment()
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    func, kwargs = extract_func(parsed_args)
    func(**kwargs)

