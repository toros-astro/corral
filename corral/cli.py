#!/usr/bin/env python
# -*- coding: utf-8 -*-

import importlib
import argparse
import abc

import six

from . import core, db, conf

# =============================================================================
# CONSTANTS
# =============================================================================

CLI_MODULE = "{}.cli".format(conf.PACKAGE)


# =============================================================================
# CLASS
# =============================================================================

@six.add_metaclass(abc.ABCMeta)
class BaseCommand(object):

    def add_arguments(self, parser):
        pass

    def ask(self, question):
        return six.moves.input(question)

    @abc.abstractmethod
    def handle(self, *args, **kwargs):
        raise NotImplementedError()


# =============================================================================
# REAL COMMANDS
# =============================================================================

class CreateDB(BaseCommand):

    options = {
        "title": "createdb"}

    def add_arguments(self, parser):
        parser.add_argument(
            "--noinput", dest="noinput", action="store_true", default=False,
            help="Create the database without asking")

    def handle(self, noinput):
        if noinput:
            answer = "yes"
        else:
            answer = self.ask(
                "Do you want to create the database[Yes/no]? ").lower()
        while answer.lower() not in ("yes", "no"):
            answer = self.ask("Please answer 'yes' or 'no': ").lower()
        if answer == "yes":
            db.create_all()


# =============================================================================
# FUNCTIONS
# =============================================================================

def create_parser():
    try:
        importlib.import_module(CLI_MODULE)
    except ImportError:
        pass

    command_names = set()

    global_parser = argparse.ArgumentParser(
        prog="corral", description="Powerful pipeline framework")
    subparsers = global_parser.add_subparsers(help="command help")

    for cls in BaseCommand.__subclasses__():
        options = getattr(cls, "options", {}) or {}
        title = options.pop("title", cls.__name__.lower())
        options["description"] = options.get("description", cls.__doc__) or ""

        if title in command_names:
            raise ValueError("Duplicate Command '{}'".format(title))
        command_names.add(title)

        parser = subparsers.add_parser(title, **options)
        command = cls()
        command.add_arguments(parser)
        parser.set_defaults(func=command.handle)

    return global_parser


def split_parsed_args(parsed_args):
    args = {
        n: getattr(parsed_args, n)
        for n in dir(parsed_args) if n != "func" and not n.startswith("_")}
    return parsed_args.func, args


def run_from_command_line(args):
    core.setup_environment()
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    func, args = split_parsed_args(parsed_args)
    func(**args)
