#!/usr/bin/env python
# -*- coding: utf-8 -*-

import importlib
import argparse
import abc
import collections
import code

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

    @classmethod
    def subclasses(cls):
        return set(cls.__subclasses__())

    @classmethod
    def collect_subclasses(cls):
        def collect(basecls):
            collected = set()
            for scls in basecls.subclasses():
                collected.add(scls)
                collected.update(scls.collect_subclasses())
            return collected
        return collect(cls)

    def add_arguments(self, parser):
        pass

    def ask(self, question):
        return six.moves.input(question)

    @abc.abstractmethod
    def handle(self, *args, **kwargs):
        raise NotImplementedError()


# =============================================================================
# BUILT-INS COMMANDS
# =============================================================================

class CreateDB(BaseCommand):
    """Create all the database structure"""

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


class Shell(BaseCommand):
    """Run the Python shell inside Corral enviroment"""

    options = {
        "title": "shell"}

    def _get_locals(self):
        slocals = {}
        slocals.update({
            cls.__name__: cls for cls in db.Model.__subclasses__()})
        if hasattr(conf.settings, "SHELL_LOCALS"):
            slocals.update(conf.settings.SHELL_LOCALS)
        return slocals

    def _create_banner(self, slocals):
        by_module = collections.defaultdict(list)
        for k, v in slocals.items():
            module_name = getattr(v, "__module__", None) or ""
            by_module[module_name].append(k)
        lines = []
        for module_name, imported in sorted(six.iteritems(by_module)):
            prefix = ", ".join(imported)
            suffix = "({})".format(module_name) if module_name else ""
            line = "LOAD: {} {}".format(prefix, suffix)
            lines.append(line)
        lines.append("-" * 80)
        return "\n".join(lines)

    def handle(self):
        slocals = self._get_locals()
        banner = self._create_banner(slocals)
        console = code.InteractiveConsole(slocals)
        console.interact(banner)


class IPython(Shell):
    """Run the IPython shell inside Corral enviroment"""

    options = {
        "title": "ipython"}

    def handle(self):
        from IPython import start_ipython
        slocals = self._get_locals()
        banner = self._create_banner(slocals)
        start_ipython(
            argv=['--TerminalInteractiveShell.banner2={}'.format(banner)],
            user_ns=slocals)


class Notebook(Shell):
    """Run the Jupyter notebook inside Corral enviroment"""

    options = {
        "title": "notebook"}

    def handle(self):
        from IPython import start_ipython
        start_ipython(argv=['notebook'])


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

    for cls in BaseCommand.collect_subclasses():
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
