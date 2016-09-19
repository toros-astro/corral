#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# DOC
# =============================================================================

"""This module contains all the built in cli commands of corral"""


# =============================================================================
# IMPORTS
# =============================================================================

import inspect
import collections
import code
import os
import logging
import sys
import argparse

import six

from texttable import Texttable

from .. import db, conf, run, creator, qa, docs
from ..libs import (
    sqlalchemy_sql_shell as sql_shell,
    argparse_ext as ape)

from .base import BaseCommand


# =============================================================================
# BUILT-INS COMMANDS
# =============================================================================

class Create(BaseCommand):
    """Create a new corral pipeline"""

    options = {
        "mode": "out"}

    def setup(self):
        self.parser.add_argument(
            "path", action="store", help="New Pipeline Path")

    def handle(self, path):
        creator.create_pipeline(path)


class CreateDB(BaseCommand):
    """Create all the database structure"""

    options = {
        "title": "createdb"}

    def setup(self):
        self.parser.add_argument(
            "--noinput", dest="noinput", action="store_true", default=False,
            help="Create the database without asking")

    def handle(self, noinput, **kwargs):
        if noinput:
            answer = "yes"
        else:
            answer = self.ask(
                "Do you want to create the database [Yes/no]? ").lower()
        while answer.lower() not in ("yes", "no"):
            answer = self.ask("Please answer 'yes' or 'no': ").lower()
        if answer == "yes":
            db.create_all()


class MakeMigrations(BaseCommand):
    """Generate a database migration script for your current pipeline

    """
    def setup(self):
        self.parser.add_argument(
            '-m', "--message", action="store", type=str,
            help="Message for the new version", dest="message")

    def handle(self, message):
        db.makemigrations(message)


class Migrate(BaseCommand):
    """Synchronizes the database state with the current
    set of models and migrations

    """

    def setup(self):
        self.parser.add_argument(
            "--noinput", dest="noinput", action="store_true", default=False,
            help="Migrate the database without asking")

    def handle(self, noinput):
        if noinput:
            answer = "yes"
        else:
            answer = self.ask(
                "Do you want to migrate the database [Yes/no]? ").lower()
        while answer.lower() not in ("yes", "no"):
            answer = self.ask("Please answer 'yes' or 'no': ").lower()
        if answer == "yes":
            db.migrate()


class Alembic(BaseCommand):
    """Execute all the Alembic migration tool commands
    under Corral enviroment

    """

    def setup(self):
        self.parser.add_argument(
            'arguments', nargs=argparse.REMAINDER,
            help="Alembic arguments (see alembic help)")

    def handle(self, arguments):
        if arguments and arguments[0] == "init":
            script = sys.argv[0]
            self.parser.error(
                    "Please use 'python {} createdb' instead".format(script))
        db.alembic(*arguments)


class Shell(BaseCommand):
    """Run the Python shell inside Corral enviroment"""

    options = {
        "title": "shell"}

    def _get_locals(self):
        slocals = {"db": db, "settings": conf.settings}
        slocals.update({
            k: v for k, v in vars(db.load_models_module()).items()
            if inspect.isclass(v) and issubclass(v, db.Model)})
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
        run.execute_loader(cls, sync=True)


class Groups(BaseCommand):
    """List all existent groups for Steps and Alerts"""

    options = {"mode": "out"}

    def handle(self):
        table = Texttable(max_width=0)
        table.set_deco(
            Texttable.BORDER | Texttable.HEADER | Texttable.VLINES)
        table.header(("Processor", "Groups"))
        table.add_row(["Steps", ":".join(run.steps_groups())])
        table.add_row(["Alerts", ":".join(run.alerts_groups()) or "-"])
        print(table.draw())


class LSSteps(BaseCommand):
    """List all available step classes"""

    options = {"mode": "out"}

    def setup(self):
        self.groups = run.steps_groups()
        self.parser.add_argument(
            "-g", "--groups", dest="groups", action="store", nargs="+",
            help="Show only steps on given groups", default=self.groups)

    def handle(self, groups):
        steps = run.load_steps(groups)
        if steps:
            table = Texttable(max_width=0)
            table.set_deco(
                Texttable.BORDER | Texttable.HEADER | Texttable.VLINES)

            table.header(("Step Class", "Process", "Groups"))
            for cls in steps:
                row = [
                    cls.__name__, cls.get_procno(),
                    ":".join(cls.get_groups())]
                table.add_row(row)

            print(table.draw())

            procs = sum(cls.get_procno() for cls in steps)
            print("  TOTAL PROCESSES: {}".format(procs))
        else:
            print("  NO STEPS FOUND")
        procs_status = (
            "Enabled" if conf.settings.DEBUG_PROCESS else "Disabled")
        print("  DEBUG PROCESS: {}\n".format(procs_status))


class Run(BaseCommand):
    """Excecute the steps in order or one step in particular"""

    options = {"title": "run"}

    def _by_name(self, name):
        if not hasattr(self, "_buff"):
            self._buff = set()
            self._mapped_cls = {cls.__name__: cls for cls in run.load_steps()}
        try:
            cls = self._mapped_cls[name]
            if cls in self._buff:
                self.parser.error("Duplicated step name '{}'".format(name))
            self._buff.add(cls)
        except KeyError:
            self.parser.error("Invalid step name '{}'".format(name))
        return cls

    def setup(self):
        group = self.parser.add_mutually_exclusive_group()
        group.add_argument(
            "-s", "--steps", dest="steps", action="store", nargs="+",
            help="Step classes name", type=self._by_name)
        group.add_argument(
            "-sg", "--step-groups", dest="groups", action="store", nargs="+",
            help="Groups To Run")

        self.parser.add_argument(
            "--sync", dest="sync", action="store_true",
            help="Execute every step synchronous", default=False)

    def handle(self, steps, groups, sync):
        if not steps:
            steps = run.load_steps(groups or None)

        procs = []
        for step_cls in steps:
            proc = run.execute_step(step_cls, sync=sync)
            procs.extend(proc)
        if not sync:
            for proc in procs:
                proc.join()
            exitcodes = [proc.exitcode for proc in procs]

            status = sum(exitcodes)
            if status:
                sys.exit(status)


class LSAlerts(BaseCommand):
    """List all available alert classes"""

    options = {"mode": "out"}

    def setup(self):
        self.groups = run.alerts_groups()
        self.parser.add_argument(
            "-g", "--groups", dest="groups", action="store", nargs="+",
            help="Show only alerts on given groups", default=self.groups)

    def handle(self, groups):
        alerts = run.load_alerts(groups)
        if alerts:
            table = Texttable(max_width=0)
            table.set_deco(
                Texttable.BORDER | Texttable.HEADER | Texttable.VLINES)

            table.header(("Alert Class", "Process", "Groups"))
            for cls in alerts:
                row = [
                    cls.__name__,  cls.get_procno(),
                    ":".join(cls.get_groups())]
                table.add_row(row)

            print(table.draw())

            procs = sum(cls.get_procno() for cls in alerts)
            print("  TOTAL PROCESSES: {}".format(procs))
        else:
            print("  NO ALERTS FOUND")
        procs_status = (
            "Enabled" if conf.settings.DEBUG_PROCESS else "Disabled")
        print("  DEBUG PROCESS: {}\n".format(procs_status))


class CheckAlerts(BaseCommand):
    """Run the alerts and announce to the endpoint if something is found"""

    options = {"title": "check-alerts"}

    def _by_name(self, name):
        if not hasattr(self, "_buff"):
            self._buff = set()
            self._mapped_cls = {cls.__name__: cls for cls in run.load_alerts()}
        try:
            cls = self._mapped_cls[name]
            if cls in self._buff:
                self.parser.error("Duplicated alert name '{}'".format(name))
            self._buff.add(cls)
        except KeyError:
            self.parser.error("Invalid alert name '{}'".format(name))
        return cls

    def setup(self):
        group = self.parser.add_mutually_exclusive_group()
        group.add_argument(
            "-a", "--alerts", dest="alerts", action="store", nargs="+",
            help="Alert classes name", type=self._by_name)
        group.add_argument(
            "-ag", "--alert-groups", dest="groups", action="store", nargs="+",
            help="Groups To Run")

        self.parser.add_argument(
            "--sync", dest="sync", action="store_true",
            help="Execute every alert synchronous", default=False)

    def handle(self, alerts, groups, sync):
        if not alerts:
            alerts = run.load_alerts(groups or None)

        procs = []
        for alert_cls in alerts:
            proc = run.execute_alert(alert_cls, sync=sync)
            procs.extend(proc)
        if not sync:
            for proc in procs:
                proc.join()
            exitcodes = [proc.exitcode for proc in procs]

            status = sum(exitcodes)
            if status:
                sys.exit(status)


class Test(BaseCommand):
    """Run all unittests for your pipeline"""

    options = {"mode": "test"}

    def _group_by_name(self, name):
        if not hasattr(self, "_buff"):
            self._buff = set()
            self._mapped_cls = {cls.__name__: cls for cls in run.load_steps()}
        try:
            cls = self._mapped_cls[name]
            if cls in self._buff:
                self.parser.error("Duplicated step name '{}'".format(name))
            self._buff.add(cls)
        except KeyError:
            self.parser.error("Invalid step name '{}'".format(name))
        return cls

    def _alert_by_name(self, name):
        if not hasattr(self, "_buff"):
            self._buff = set()
            self._mapped_cls = {cls.__name__: cls for cls in run.load_alerts()}
        try:
            cls = self._mapped_cls[name]
            if cls in self._buff:
                self.parser.error("Duplicated alert name '{}'".format(name))
            self._buff.add(cls)
        except KeyError:
            self.parser.error("Invalid alert name '{}'".format(name))
        return cls

    def setup(self):
        self.parser.add_argument(
            "-f", "--failfast", dest='failfast', default=False,
            help='Stop on first fail or error', action='store_true')

        self.parser.add_argument(
            "-dl", "--default-logging", dest='default_logging', default=False,
            help='If is false all the loggers are setted to WARNING',
            action='store_true')

        verbose_group = self.parser.add_mutually_exclusive_group()
        verbose_group.add_argument(
            "-v", "--verbose", dest='verbosity',  default=0, const=1,
            help='Verbose output', action='store_const')
        verbose_group.add_argument(
            "-vv", "--vverbose", dest='verbosity', const=2,
            help='Verbose output', action='store_const')

        self.parser.add_argument(
            "-el", "--exclude-loader", dest="exclude_loader", default=False,
            help="Exclude loader from QA run", action="store_true")

        steps_group = self.parser.add_mutually_exclusive_group()
        steps_group.add_argument(
            "-es", "--exclude-steps", dest="exclude_steps", default=False,
            help="Exclude steps from QA run", action="store_true")
        steps_group.add_argument(
            "-s", "--steps", dest="steps", action="store", nargs="+",
            help="Step classes name", type=self._group_by_name)
        steps_group.add_argument(
            "-sg", "--step-groups", dest="step_groups", action="store",
            nargs="+", help="Groups To tests")

        alerts_group = self.parser.add_mutually_exclusive_group()
        alerts_group.add_argument(
            "-ea", "--exclude-alerts", dest="exclude_alerts", default=False,
            help="Exclude alerts from QA run", action="store_true")
        alerts_group.add_argument(
            "-a", "--alerts", dest="alerts", action="store", nargs="+",
            help="Alert classes name", type=self._alert_by_name)
        alerts_group.add_argument(
            "-ag", "--alert-groups", dest="alert_groups", action="store",
            nargs="+", help="Groups to tests")

    def handle(self, failfast, verbosity, default_logging, exclude_loader,
               exclude_steps, steps, step_groups,
               exclude_alerts, alerts, alert_groups):

        processors = []
        if not exclude_loader:
            processors.append(run.load_loader())

        if not exclude_steps:
            if not steps:
                steps = run.load_steps(step_groups or None)
            processors.extend(steps or [])

        if not exclude_alerts:
            if not alerts:
                alerts = run.load_alerts(alert_groups or None)
            processors.extend(alerts or [])

        result = qa.run_tests(processors, failfast, verbosity, default_logging)
        if not result.wasSuccessful():
            self.exit_with(1)


class QAReport(BaseCommand):
    """Run the QA test for your pipeline and make a reports of
    errors, maintanability, coverage and a full QA index.

    """

    options = {"mode": "test"}
    epilogue = ("To convert your documentation to more suitable formats "
                "we sugest Pandoc (http://pandoc.org/). Example: \n"
                " $ pandoc {filename} -o {basename}.html # HTML\n"
                " $ pandoc {filename} -o {basename}.tex  # LaTeX\n"
                " $ pandoc {filename} -o {basename}.pdf  # PDF via LaTeX")

    def setup(self):
        self.parser.add_argument(
            "-o", "--output", dest="out", nargs="?",
            type=ape.FileType('w'), default=sys.stdout,
            action="store", help="destination of the diagram")
        self.parser.add_argument(
            "--not-explain-qai", dest="explain_qai",
            default=True,  action="store_false",
            help="Exclude the explanation the Corral QAI and QAI Score")
        self.parser.add_argument(
            "--exclude-test-output", "-et", dest='full_output', default=True,
            help='Add the full outut of test into the report',
            action='store_false')

        self.parser.add_argument(
            "-dl", "--default-logging", dest='default_logging', default=False,
            help='If is false all the loggers are setted to WARNING',
            action='store_true')

    def handle(self, out, explain_qai, full_output, default_logging):
        processors = []
        processors.append(run.load_loader())
        processors.extend(run.load_steps(None))
        processors.extend(run.load_alerts(None))
        report = qa.qa_report(processors, default_logging=default_logging)

        data = docs.qa_report(
            report=report, full_output=full_output, explain_qai=explain_qai)

        out.write(data)
        if out == sys.stdout:
            print("\n")
        else:
            basename = os.path.basename(out.name).rsplit(".", 1)[0]
            print("Your documentaton file '{}' was created.".format(out.name))
            print("")
            print(self.epilogue.format(filename=out.name, basename=basename))
            print("")


class CreateModelsDiagram(BaseCommand):
    """Generates a class diagram in 'dot'
    format of the models classes"""

    options = {"mode": "out", "title": "create-models-diagram"}
    epilogue = (
        "Render graph by graphviz:\n"
        " $ dot -Tpng {filename} > {basename}.png\n"
        "\nMore Help: http://www.graphviz.org/")

    def setup(self):
        self.parser.add_argument(
            "-o", "--output", dest="out", nargs="?",
            type=ape.FileType('w'), default=sys.stdout,
            action="store", help="destination of the diagram")

    def handle(self, out):
        data = docs.models_diagram(fmt="dot")
        out.write(data)
        if out == sys.stdout:
            print("\n")
        else:
            basename = os.path.basename(out.name).rsplit(".", 1)[0]
            print("Your graph file '{}' was created.".format(out.name))
            print("")
            print(self.epilogue.format(filename=out.name, basename=basename))
            print("")


class CreateDoc(BaseCommand):
    """Generate a Markdown documentation for your pipeline"""

    options = {"mode": "out", "title": "create-doc"}
    epilogue = ("To convert your documentation to more suitable formats "
                "we sugest Pandoc (http://pandoc.org/). Example: \n"
                " $ pandoc {filename} -o {basename}.html # HTML\n"
                " $ pandoc {filename} -o {basename}.tex  # LaTeX\n"
                " $ pandoc {filename} -o {basename}.pdf  # PDF via LaTeX")

    def setup(self):
        self.parser.add_argument(
            "-o", "--output", dest="out", nargs="?",
            type=ape.FileType('w'), default=sys.stdout,
            action="store", help="destination of the diagram")

    def handle(self, out):
        processors = []
        processors.append(run.load_loader())
        processors.extend(run.load_steps(None))
        processors.extend(run.load_alerts(None))

        models = db.get_models(default=False)

        doc = docs.create_doc(processors, models)

        out.write(doc)
        if out == sys.stdout:
            print("\n")
        else:
            basename = os.path.basename(out.name).rsplit(".", 1)[0]
            print("Your documentaton file '{}' was created.".format(out.name))
            print("")
            print(self.epilogue.format(filename=out.name, basename=basename))
            print("")


#~ class CreatePipelineDiagram(BaseCommand):
    #~ """Generates a pipeline diagram diagram in 'dot' format"""

    #~ options = {"mode": "out", "title": "create-pipeline-diagram"}
    #~ epilogue = (
        #~ "Render graph by graphviz:\n"
        #~ " $ dot -Tpng {filename} > {basename}.png\n"
        #~ "\nMore Help: http://www.graphviz.org/")

    #~ def setup(self):
        #~ self.parser.add_argument(
            #~ "-o", "--output", dest="out", nargs="?",
            #~ type=ape.FileType('w'), default=sys.stdout,
            #~ action="store", help="destination of the diagram")

    #~ def handle(self, out):
        #~ data = docs.pipeline_diagram()
        #~ out.write(data)
        #~ if out == sys.stdout:
            #~ print("\n")
        #~ else:
            #~ basename = os.path.basename(out.name).rsplit(".", 1)[0]
            #~ print("Your graph file '{}' was created.".format(out.name))
            #~ print("")
            #~ print(self.epilogue.format(filename=out.name, basename=basename))
            #~ print("")
