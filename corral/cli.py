#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import abc
import collections
import code

import six

from . import core, db, conf, util, run


# =============================================================================
# CONSTANTS
# =============================================================================

CLI_MODULE = "{}.cli".format(conf.PACKAGE)


# =============================================================================
# CLASS
# =============================================================================

@six.add_metaclass(abc.ABCMeta)
class BaseCommand(object):

    def setup(self):
        pass

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

    def run_plain(self, slocals, banner):
        console = code.InteractiveConsole(slocals)
        console.interact(banner)

    def run_ipython(self, slocals, banner):
        from IPython import start_ipython
        start_ipython(
            argv=['--TerminalInteractiveShell.banner2={}'.format(banner)],
            user_ns=slocals)

    def run_bpython(self, slocals, banner):
        from bpython import embed
        embed(locals_=slocals, banner=banner)

    def setup(self):
        self.shells = collections.OrderedDict()
        try:
            import IPython
            self.shells["ipython"] = self.run_ipython
        except ImportError:
            pass
        try:
            import bpython
            self.shells["bpython"] = self.run_bpython
        except ImportError:
            pass
        self.shells["plain"] = self.run_plain

    def add_arguments(self, parser):
        parser.add_argument(
            "--shell", "-s", dest="shell", action="store",
            choices=self.shells.keys(), default=self.shells.keys()[0],
            help="Specify the shell to be used")

    def handle(self, shell):
        slocals = self._get_locals()
        banner = self._create_banner(slocals)
        shell = self.shells[shell]
        shell(slocals, banner)


class Notebook(BaseCommand):
    """Run the Jupyter notebook inside Corral enviroment"""

    options = {
        "title": "notebook"}

    def handle(self):
        from IPython import start_ipython
        start_ipython(argv=['notebook'])


class Load(BaseCommand):
    """Excecute the loader class"""

    options = {"title": "load"}

    def handle(self):
        cls = run.load_loader()
        run.execute_loader(cls)


# =============================================================================
# FUNCTIONS
# =============================================================================

def create_parser():
    if conf.settings.has_module("cli"):
        try:
            util.dimport(CLI_MODULE)
        except ImportError as err:
            core.logger.error(six.text_type(err))

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
        command = cls()
        command.setup()
        command.add_arguments(parser)
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
