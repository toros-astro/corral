#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module contains all the buil in cli commands of corral"""


# =============================================================================
# IMPORTS
# =============================================================================

import collections
import code
import os
import logging
import sys

import six

from .. import db, conf, run
from ..libs import sqlalchemy_sql_shell as sql_shell

from .base import BaseCommand


# =============================================================================
# BUILT-INS COMMANDS
# =============================================================================

class CreateDB(BaseCommand):
    """Create all the database structure"""

    options = {
        "title": "createdb"}

    def setup(self):
        self.parser.add_argument(
            "--noinput", dest="noinput", action="store_true", default=False,
            help="Create the database without asking")

    def handle(self, noinput):
        if noinput:
            answer = "yes"
        else:
            answer = self.ask(
                "Do you want to create the database [Yes/no]? ").lower()
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
            import IPython  # noqa
            self.shells["ipython"] = self.run_ipython
        except ImportError:
            pass
        try:
            import bpython  # noqa
            self.shells["bpython"] = self.run_bpython
        except ImportError:
            pass
        self.shells["plain"] = self.run_plain

        self.parser.add_argument(
            "--shell", "-s", dest="shell", action="store",
            choices=self.shells.keys(), default=list(self.shells.keys())[0],
            help="Specify the shell to be used")

    def handle(self, shell):
        slocals = self._get_locals()
        with db.session_scope() as session:
            slocals["session"] = session
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


class DBShell(BaseCommand):
    """Run an SQL shell throught sqlalchemy"""

    options = {"title": "dbshell"}

    def handle(self):
        elogger = logging.getLogger('sqlalchemy.engine')
        original_level = elogger.level
        try:
            elogger.setLevel(logging.WARNING)
            print("Connected to: {}".format(db.engine))
            sql_shell.run(db.engine)
        finally:
            elogger.setLevel(original_level)


class Exec(BaseCommand):
    """Execute file inside corral environment"""

    options = {"title": "exec"}

    def setup(self):
        self.parser.add_argument("path", action="store", help="Path to script")

    def handle(self, path):
        ns = {}
        fname = os.path.basename(path)
        with open(path) as fp:
            code = compile(fp.read(), fname, 'exec')
            exec(code, ns, ns)


class Load(BaseCommand):
    """Excecute the loader class"""

    options = {"title": "load"}

    def handle(self):
        cls = run.load_loader()
        proc = run.execute_loader(cls, sync=True)
        sys.exit(proc.exitcode)


class Run(BaseCommand):
    """Excecute the steps in order or one step in particular"""

    OPTIONS = {"title": "run"}

    def _step_classes(self, class_name):
        if class_name in self.buff:
            self.parser.error("Duplicated step name '{}'".format(class_name))
        self.buff.add(class_name)
        try:
            return self.mapped_steps[class_name]
        except KeyError:
            self.parser.error("Invalid step name '{}'".format(class_name))

    def setup(self):
        self.all_steps = run.load_steps()
        self.mapped_steps = {cls.__name__: cls for cls in self.all_steps}
        self.buff = set()

        self.parser.add_argument(
            "--steps", dest="step_classes", action="store", nargs="+",
            help="Step class name", default=self.all_steps,
            type=self._step_classes)
        self.parser.add_argument(
            "--sync", dest="sync", action="store_true",
            help="Execute every step synchronous", default=False)

    def handle(self, step_classes, sync):
        procs = []
        for step_cls in step_classes:
            proc = run.execute_step(step_cls, sync)
            procs.append(proc)
        if not sync:
            for proc in procs:
                proc.join()
        exitcodes = [proc.exitcode for proc in procs]

        status = sum(exitcodes)
        sys.exit(status)
