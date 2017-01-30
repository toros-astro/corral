#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016-2017, Cabral, Juan; Sanchez, Bruno & Berois, Martín
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# * Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.

# * Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


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
import shutil

import six

from texttable import Texttable

from .. import db, run, creator, qa, docs, cli, setup, res, util
from ..libs import (
    sqlalchemy_sql_shell as sql_shell,
    argparse_ext as ape)

from .base import BaseCommand

conf = util.dimport("corral.conf", lazy=True)


# =============================================================================
# BUILT-INS COMMANDS
# =============================================================================

class Create(BaseCommand):
    """Create a new corral pipeline"""

    options = {
        "mode": "nopipe"}

    def setup(self):
        from .. import core

        logging.basicConfig(format='[%(levelname)s] %(message)s')
        core.logger.setLevel(logging.INFO)
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
            '-m', "--message", action="store", type=str, required=True,
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

    def get_locals(self):
        slocals = {"db": db, "settings": conf.settings}
        slocals.update({
            k: v for k, v in vars(db.load_models_module()).items()
            if inspect.isclass(v) and issubclass(v, db.Model)})
        if hasattr(conf.settings, "SHELL_LOCALS"):
            slocals.update(conf.settings.SHELL_LOCALS)
        return slocals

    def create_banner(self, slocals):
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
        slocals = self.get_locals()
        with db.session_scope() as session:
            slocals["session"] = session
            banner = self.create_banner(slocals)
            shell = self.shells[shell]
            shell(slocals, banner)


class Notebook(BaseCommand):
    """Run the Jupyter notebook inside Corral enviroment"""

    options = {
        "title": "notebook",
        "mode": "out"}

    def install_kernel_spec(self, app, dir_name, display_name,
                            settings_module, ipython_arguments):
        """install an IPython >= 3.0 kernelspec that loads corral env

        Thanks: django extensions

        """
        ksm = app.kernel_spec_manager
        try_spec_names = ['python3' if six.PY3 else 'python2', 'python']
        if isinstance(try_spec_names, six.string_types):
            try_spec_names = [try_spec_names]
        ks = None
        for spec_name in try_spec_names:
            try:
                ks = ksm.get_kernel_spec(spec_name)
                break
            except:
                continue
        if not ks:
            self.parser.error("No notebook (Python) kernel specs found")

        ks.display_name = display_name
        ks.env["CORRAL_SETTINGS_MODULE"] = settings_module
        ks.argv.extend(ipython_arguments)

        in_corral_dir, in_corral = os.path.split(os.path.realpath(sys.argv[0]))

        pythonpath = ks.env.get(
            'PYTHONPATH', os.environ.get('PYTHONPATH', ''))
        pythonpath = pythonpath.split(':')
        if in_corral_dir not in pythonpath:
            pythonpath.append(in_corral_dir)
        ks.env['PYTHONPATH'] = ':'.join(filter(None, pythonpath))

        kernel_dir = os.path.join(ksm.user_kernel_dir, conf.PACKAGE)
        if not os.path.exists(kernel_dir):
            os.makedirs(kernel_dir)
            shutil.copy(res.fullpath("logo-64x64.png"), kernel_dir)
        with open(os.path.join(kernel_dir, 'kernel.json'), 'w') as f:
            f.write(ks.to_json())

    def setup(self):
        self.parser.add_argument(
            'arguments', nargs=argparse.REMAINDER,
            help="Notebook arguments (see notebook help)")

    def handle(self, arguments):
        try:
            from notebook.notebookapp import NotebookApp
        except ImportError:  # pragma: no cover
            self.parser.error("notebook not found. Please install it")
        else:
            extension = "corral.libs.notebook_extension"

            pipeline = setup.load_pipeline_setup()

            app = NotebookApp.instance()
            dir_name = conf.PACKAGE
            display_name = pipeline.name
            settings_module = conf.CORRAL_SETTINGS_MODULE

            ipython_arguments = ['--ext', extension]

            app.initialize(arguments)
            self.install_kernel_spec(
                app, dir_name, display_name,
                settings_module, ipython_arguments)
            app.start()


class DBShell(BaseCommand):
    """Run an SQL shell throught sqlalchemy"""

    options = {"title": "dbshell"}

    def run_plain(self):
        elogger = logging.getLogger('sqlalchemy.engine')
        original_level = elogger.level
        try:
            elogger.setLevel(logging.WARNING)
            print("Connected to: {}".format(db.engine))
            sql_shell.run(db.engine)
        finally:
            elogger.setLevel(original_level)

    def run_pgcli(self):
        from pgcli import main
        pgcli = main.PGCli()
        pgcli.connect(
            database=self.urlo.database, host=self.urlo.host or '',
            user=self.urlo.username or '',
            port=self.urlo.port or '',
            passwd=self.urlo.password or '')
        pgcli.run_cli()

    def run_mycli(self):
        from mycli import main
        mycli = main.MyCli()
        mycli.connect(
            database=self.urlo.database, host=self.urlo.host or '',
            user=self.urlo.username or '',
            port=self.urlo.port or '',
            passwd=self.urlo.password or '')
        mycli.run_cli()

    def setup(self):
        self.shells = collections.OrderedDict()
        self.urlo = db.get_urlo()
        backend = self.urlo.get_backend_name()
        if backend == "postgresql":
            try:
                import pgcli  # noqa
                self.shells["adv"] = self.run_pgcli
            except ImportError:  # pragma: no cover
                pass
        elif backend == "mysql":
            try:
                import mycli  # noqa
                self.shells["adv"] = self.run_mycli
            except ImportError:  # pragma: no cover
                pass
        else:
            self.shells["adv"] = self.run_plain
        self.shells["plain"] = self.run_plain

        self.parser.add_argument(
            "--shell", "-s", dest="shell", action="store",
            choices=self.shells.keys(), default=list(self.shells.keys())[0],
            help="Specify the shell to be used")

    def handle(self, shell):
        shell = self.shells[shell]
        shell()


class Exec(BaseCommand):
    """Execute file inside corral environment"""

    options = {"title": "exec"}

    def setup(self):
        self.parser.add_argument("path", action="store", help="Path to script")

    def handle(self, path):
        fname, ns = os.path.basename(path), {}
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


class RunAll(BaseCommand):
    """Shortcut command to run the loader, steps and alerts asynchronous.

    For more control check the commands 'load', 'run' and 'check-alerts'.

    """

    options = {"title": "run-all"}

    def handle(self):
        procs = []

        loader_runner = [run.load_loader()], run.execute_loader
        steps_runner = run.load_steps(), run.execute_step
        alerts_runner = run.load_alerts(), run.execute_alert

        for processors, runner in [loader_runner, steps_runner, alerts_runner]:
            for processor in processors:
                proc = runner(processor)
                procs.extend(proc)
        for proc in procs:
            proc.join()
        exitcodes = [proc.exitcode for proc in procs]
        status = sum(exitcodes)
        if status:
            sys.exit(status)


class Test(BaseCommand):
    """Run all unittests for your pipeline"""

    options = {"mode": "test"}

    def _step_by_name(self, name):
        if not hasattr(self, "_sbuff"):
            self._sbuff = set()
            self._smapped_cls = {cls.__name__: cls for cls in run.load_steps()}
        try:
            cls = self._smapped_cls[name]
            if cls in self._sbuff:
                self.parser.error("Duplicated step name '{}'".format(name))
            self._sbuff.add(cls)
        except KeyError:
            self.parser.error("Invalid step name '{}'".format(name))
        return cls

    def _alert_by_name(self, name):
        if not hasattr(self, "_abuff"):
            self._abuff = set()
            self._amapped_cls = {
                cls.__name__: cls for cls in run.load_alerts()}
        try:
            cls = self._amapped_cls[name]
            if cls in self._abuff:
                self.parser.error("Duplicated alert name '{}'".format(name))
            self._abuff.add(cls)
        except KeyError:
            self.parser.error("Invalid alert name '{}'".format(name))
        return cls

    def _command_by_name(self, name):
        if not hasattr(self, "_cbuff"):
            self._cbuff = set()
            self._cmapped_cls = {
                cls.__name__: cls for cls in cli.load_project_commands()}
        try:
            cls = self._cmapped_cls[name]
            if cls in self._cbuff:
                self.parser.error("Duplicated command name '{}'".format(name))
            self._cbuff.add(cls)
        except KeyError:
            self.parser.error("Invalid command name '{}'".format(name))
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
            help="Step classes name", type=self._step_by_name)
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

        cmd_group = self.parser.add_mutually_exclusive_group()
        cmd_group.add_argument(
            "-ec", "--exclude-commands", dest="exclude_cmds", default=False,
            help="Exclude commands from QA run", action="store_true")
        cmd_group.add_argument(
            "-c", "--commands", dest="commands", action="store", nargs="+",
            help="Commands classes name", type=self._command_by_name)

    def handle(self, failfast, verbosity, default_logging, exclude_loader,
               exclude_steps, steps, step_groups,
               exclude_alerts, alerts, alert_groups,
               exclude_cmds, commands):

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

        if not exclude_cmds:
            if not commands:
                commands = cli.load_project_commands()

        result = qa.run_tests(
            processors, commands, failfast, verbosity, default_logging)
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
            help='Add the full output of test into the report',
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

        commands = cli.load_project_commands()

        report = qa.qa_report(
            processors, commands, default_logging=default_logging)

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
        out.flush()


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
        out.flush()


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
            action="store", help="destination of the documentation")

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
        out.flush()
