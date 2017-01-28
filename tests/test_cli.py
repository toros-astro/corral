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

"""All command line interfaces tests"""


# =============================================================================
# IMPORTS
# =============================================================================

import os

import mock

from corral import cli, run, db, exceptions
from corral.cli import commands as builtin_commands

from . import commands
from .steps import TestLoader, Step1, Step2
from .alerts import Alert1
from .base import BaseTest


# =============================================================================
# BASE CLASS
# =============================================================================

class TestCli(BaseTest):

    def test_command_ask(self, *args):
        with mock.patch("six.moves.input") as sinput:
            cmd = commands.TestAPICommand()
            cmd.configure(mock.Mock())
            cmd.setup()
            cmd.ask("foo")
            sinput.assert_called_once_with("foo")

    @mock.patch("sys.stderr")
    @mock.patch("sys.stdout")
    def test_load_commands_module(self, *args):
        actual = cli.load_commands_module()
        self.assertIs(actual, commands)

        with mock.patch("corral.util.dimport", side_effect=ImportError()):
            actual = cli.load_commands_module()
            self.assertIsNone(actual)

        with mock.patch("corral.util.dimport", side_effect=Exception()):
            with self.assertRaises(Exception):
                cli.load_commands_module()

    @mock.patch("corral.core.setup_environment")
    def test_duplicate_title(self, *args):
        patch = "tests.commands.TestAPICommand.options"
        with mock.patch.dict(patch, {"title": "exec"}):
            with self.assertRaises(exceptions.ImproperlyConfigured):
                cli.run_from_command_line()

    @mock.patch("sys.argv", new=["test", "foo"])
    def test_command_api(self, *args):
        with mock.patch("corral.core.setup_environment") as setup_environment:
            with mock.patch("tests.commands.TestAPICommand.setup") as setup:
                with mock.patch("tests.commands.TestAPICommand.handle") as hdl:
                    cli.run_from_command_line()
                    self.assertTrue(setup_environment.called)
                    self.assertTrue(setup.called)
                    self.assertTrue(hdl.called)

    @mock.patch("corral.core.setup_environment")
    @mock.patch("tests.commands.TestAPICommand.handle", side_effect=Exception)
    @mock.patch("sys.stderr")
    @mock.patch("sys.stdout")
    def test_stack_trace_option(self, *args):
        with mock.patch("sys.argv", new=["test",  "--stacktrace", "foo"]):
            with self.assertRaises(Exception):
                cli.run_from_command_line()
        with mock.patch("sys.argv", new=["test", "foo"]):
            cli.run_from_command_line()

    @mock.patch("sys.argv", new=["test", "exit_error"])
    def test_exit_error(self, *args):
        with mock.patch("corral.core.setup_environment"):
            with mock.patch("sys.exit") as sys_exit:
                cli.run_from_command_line()
                sys_exit.assert_called_once_with(
                    commands.TestExitErrorCommand.EXIT_STATUS)


class Create(BaseTest):

    @mock.patch("sys.argv", new=["test", "create", "foo"])
    @mock.patch("corral.creator.create_pipeline")
    def test_create_comand(self, create_pipeline):
        cli.run_from_command_line()
        create_pipeline.assert_called_with("foo")

    @mock.patch("corral.creator.create_pipeline", side_effect=Exception)
    @mock.patch("sys.stderr")
    def test_stack_trace_option(self, *args):
        with mock.patch("sys.argv",
                        new=["test", "--stacktrace", "create", "foo"]):
            with self.assertRaises(Exception):
                cli.run_from_command_line()
        with mock.patch("sys.argv", new=["test", "create", "foo"]):
            cli.run_from_command_line()


class CreateDB(BaseTest):

    @mock.patch("sys.argv", new=["test", "createdb"])
    @mock.patch("corral.core.setup_environment")
    @mock.patch("corral.db.alembic")
    def test_create_db_comand(self, *args):
        patch = "corral.cli.commands.CreateDB.ask"
        with mock.patch(patch, return_value="yes") as ask:
            with mock.patch("corral.db.create_all") as create_all:
                cli.run_from_command_line()
                self.assertTrue(ask.called)
                self.assertTrue(create_all.called)

        with mock.patch(patch, return_value="no") as ask:
            with mock.patch("corral.db.create_all") as create_all:
                cli.run_from_command_line()
                self.assertTrue(ask.called)
                create_all.assert_not_called()

        with mock.patch(patch, side_effect=["foo", "no"]) as ask:
            with mock.patch("corral.db.create_all") as create_all:
                cli.run_from_command_line()
                expected = [
                    mock.call(arg) for arg in
                    ("Do you want to create the database [Yes/no]? ",
                     "Please answer 'yes' or 'no': ")]
                ask.assert_has_calls(expected)
                self.assertFalse(create_all.called)

    @mock.patch("sys.argv", new=["test", "createdb", "--noinput"])
    @mock.patch("corral.core.setup_environment")
    @mock.patch("corral.db.alembic")
    def test_create_db_comand_noinput(self, *args):
        patch = "corral.cli.commands.CreateDB.ask"
        with mock.patch(patch, return_value="yes") as ask:
            with mock.patch("corral.db.create_all") as create_all:
                cli.run_from_command_line()
                ask.assert_not_called()
                self.assertTrue(create_all.called)

        with mock.patch(patch, return_value="no") as ask:
            with mock.patch("corral.db.create_all") as create_all:
                cli.run_from_command_line()
                ask.assert_not_called()
                self.assertTrue(create_all.called)


class MakeMigrations(BaseTest):

    @mock.patch("sys.argv", new=["test", "makemigrations", "-m", "foo"])
    @mock.patch("corral.core.setup_environment")
    def test_makemigrations(self, *args):
        with mock.patch("corral.db.makemigrations") as makemigrations:
            cli.run_from_command_line()
            makemigrations.assert_called_with("foo")


class Migrate(BaseTest):

    @mock.patch("sys.argv", new=["test", "migrate"])
    @mock.patch("corral.core.setup_environment")
    def test_migrate_comand(self, *args):
        patch = "corral.cli.commands.Migrate.ask"
        with mock.patch(patch, return_value="yes") as ask:
            with mock.patch("corral.db.migrate") as migrate:
                cli.run_from_command_line()
                ask.assert_called()
                migrate.assert_called()

        with mock.patch(patch, return_value="no") as ask:
            with mock.patch("corral.db.migrate") as migrate:
                cli.run_from_command_line()
                self.assertTrue(ask.called)
                migrate.assert_not_called()

        with mock.patch(patch, side_effect=["foo", "no"]) as ask:
            with mock.patch("corral.db.migrate") as migrate:
                cli.run_from_command_line()
                expected = [
                    mock.call(arg) for arg in
                    ("Do you want to migrate the database [Yes/no]? ",
                     "Please answer 'yes' or 'no': ")]
                ask.assert_has_calls(expected)
                self.assertFalse(migrate.called)

    @mock.patch("sys.argv", new=["test", "migrate", "--noinput"])
    @mock.patch("corral.core.setup_environment")
    def test_migrate_noinput(self, *args):
        patch = "corral.cli.commands.Migrate.ask"
        with mock.patch(patch, return_value="yes") as ask:
            with mock.patch("corral.db.migrate") as migrate:
                cli.run_from_command_line()
                ask.assert_not_called()
                self.assertTrue(migrate.called)

        with mock.patch(patch, return_value="no") as ask:
            with mock.patch("corral.db.migrate") as migrate:
                cli.run_from_command_line()
                ask.assert_not_called()
                self.assertTrue(migrate.called)


class Alembic(BaseTest):

    @mock.patch("sys.argv", new=["test", "alembic", "foo"])
    @mock.patch("corral.core.setup_environment")
    @mock.patch("corral.db.alembic")
    def test_alembic(self, alembic, *args):
            cli.run_from_command_line()
            alembic.assert_called_with("foo")

    @mock.patch("sys.argv", new=["test", "alembic", "init"])
    @mock.patch("corral.core.setup_environment")
    @mock.patch("corral.db.alembic")
    @mock.patch("sys.stderr")
    def test_alembic_fail_init(self, stderr, *args):
            cli.run_from_command_line()
            stderr.write.assert_called()


class Shell(BaseTest):

    @mock.patch("sys.argv", new=["test", "shell"])
    @mock.patch("corral.core.setup_environment")
    def test_default_shell_command(self, *args):
        mockeable_shell_calls = {
            "ipython": "IPython.start_ipython",
            "bpython": "bpython.embed",
            "plain": "code.InteractiveConsole.interact",
        }

        shell_cmd = builtin_commands.Shell()
        shell_cmd.configure(mock.Mock())
        shell_cmd.setup()
        shells = shell_cmd.shells

        first_shell = tuple(shells.keys())[0]
        to_mock = mockeable_shell_calls[first_shell]

        with mock.patch(to_mock) as call:
            cli.run_from_command_line()
            self.assertTrue(call.called)

    @mock.patch("sys.argv", new=["test", "shell", "--shell", "ipython"])
    @mock.patch("corral.core.setup_environment")
    def test_ipython(self, *args):
        with mock.patch("IPython.start_ipython") as start_ipython:
            cli.run_from_command_line()
            self.assertTrue(start_ipython.called)

    @mock.patch("sys.argv", new=["test", "shell", "--shell", "bpython"])
    @mock.patch("corral.core.setup_environment")
    def test_bpython(self, *args):
        with mock.patch("bpython.embed") as embed:
            cli.run_from_command_line()
            self.assertTrue(embed.called)

    @mock.patch("sys.argv", new=["test", "shell", "--shell", "plain"])
    @mock.patch("corral.core.setup_environment")
    def test_plain(self, *args):
        with mock.patch("code.InteractiveConsole.interact") as interact:
            cli.run_from_command_line()
            self.assertTrue(interact.called)

    @mock.patch("sys.argv", new=["test", "shell"])
    @mock.patch("corral.core.setup_environment")
    def test_fails_ipython_fails(self, *args):
        original = builtin_commands.Shell.run_ipython
        property_mock = mock.PropertyMock(side_effect=ImportError)
        try:
            builtin_commands.Shell.run_ipython = property_mock
            shell_cmd = builtin_commands.Shell()
            shell_cmd.configure(mock.Mock())
            shell_cmd.setup()
            with mock.patch("bpython.embed") as embed:
                cli.run_from_command_line()
                self.assertTrue(embed.called)
        finally:
            builtin_commands.Shell.run_ipython = original

    @mock.patch("sys.argv", new=["test", "shell"])
    @mock.patch("corral.core.setup_environment")
    def test_import_bpython_fails(self, *args):
        original = builtin_commands.Shell.run_bpython
        property_mock = mock.PropertyMock(side_effect=ImportError)
        try:
            builtin_commands.Shell.run_bpython = property_mock
            shell_cmd = builtin_commands.Shell()
            shell_cmd.configure(mock.Mock())
            shell_cmd.setup()
            with mock.patch("IPython.start_ipython") as start_ipython:
                cli.run_from_command_line()
                self.assertTrue(start_ipython.called)
        finally:
            builtin_commands.Shell.run_bpython = original

    @mock.patch("sys.argv", new=["test", "shell"])
    @mock.patch("corral.core.setup_environment")
    def test_import_ipython_and_bpython_fails(self, *args):
        ioriginal = builtin_commands.Shell.run_ipython
        boriginal = builtin_commands.Shell.run_bpython
        property_mock = mock.PropertyMock(side_effect=ImportError)
        try:
            builtin_commands.Shell.run_ipython = property_mock
            builtin_commands.Shell.run_bpython = property_mock
            shell_cmd = builtin_commands.Shell()
            shell_cmd.configure(mock.Mock())
            shell_cmd.setup()
            with mock.patch("code.InteractiveConsole.interact") as interact:
                cli.run_from_command_line()
                self.assertTrue(interact.called)
        finally:
            builtin_commands.Shell.run_ipython = ioriginal
            builtin_commands.Shell.run_bpython = boriginal


class DBShell(BaseTest):

    @mock.patch("sys.argv", new=["test", "dbshell"])
    @mock.patch("corral.core.setup_environment")
    def test_dbshell(self, *args):
        with mock.patch("corral.libs.sqlalchemy_sql_shell.run") as run_dbshell:
            with mock.patch("sys.stdout"):
                cli.run_from_command_line()
                run_dbshell.assert_called_with(db.engine)

    @mock.patch("sys.argv", new=["test", "dbshell"])
    @mock.patch("corral.core.setup_environment")
    @mock.patch("tests.settings.CONNECTION", "postgresql://usr:psw@host:1/db")
    def test_dbshell_pgcli(self, *args):
        with mock.patch("pgcli.main.PGCli") as run_dbshell:
            with mock.patch("sys.stdout"):
                cli.run_from_command_line()
                run_dbshell.assert_called()
                run_dbshell().connect.assert_called_with(
                    database="db", host="host",
                    passwd="psw", port=1, user="usr")
                run_dbshell().run_cli.assert_called()

    @mock.patch("sys.argv", new=["test", "dbshell"])
    @mock.patch("corral.core.setup_environment")
    @mock.patch("tests.settings.CONNECTION", "mysql://usr:psw@host:1/db")
    def test_dbshell_mycli(self, *args):
        with mock.patch("mycli.main.MyCli") as run_dbshell:
            with mock.patch("sys.stdout"):
                cli.run_from_command_line()
                run_dbshell.assert_called()
                run_dbshell().connect.assert_called_with(
                    database="db", host="host",
                    passwd="psw", port=1, user="usr")
                run_dbshell().run_cli.assert_called()


class Exec(BaseTest):

    @mock.patch("corral.core.setup_environment")
    def test_execfile(self, *args):
        path = os.path.abspath(os.path.dirname(__file__))
        script = os.path.join(path, "script.py")
        with mock.patch("sys.argv", new=["test", "exec", script]):
            cli.run_from_command_line()


class Notebook(BaseTest):

    @mock.patch("sys.argv", new=["test", "notebook"])
    @mock.patch("corral.core.setup_environment")
    @mock.patch("corral.cli.commands.Notebook.install_kernel_spec")
    def test_notebook_command(self, *args):
        with mock.patch("notebook.notebookapp.NotebookApp.instance") as nb:
            cli.run_from_command_line()
            self.assertTrue(nb.called)


class Load(BaseTest):

    @mock.patch("sys.argv", new=["test", "load"])
    @mock.patch("corral.core.setup_environment")
    def test_load(self, *args):
        with mock.patch("corral.run.execute_loader") as execute_loader:
            cli.run_from_command_line()
            execute_loader.assert_called_with(TestLoader, sync=True)


class Groups(BaseTest):

    @mock.patch("sys.argv", new=["test", "groups"])
    @mock.patch("corral.core.setup_environment")
    @mock.patch("sys.stdout")
    def test_groups(self, *args):
        with mock.patch("texttable.Texttable.header") as header, \
             mock.patch("texttable.Texttable.add_row") as row:
            cli.run_from_command_line()
            header.assert_called_with(("Processor", "Groups"))
            row.assert_any_call(["Steps", ":".join(run.steps_groups())])
            row.assert_any_call(["Alerts", ":".join(run.alerts_groups())])


class LSSteps(BaseTest):

    @mock.patch("sys.argv", new=["test", "lssteps"])
    @mock.patch("corral.core.setup_environment")
    @mock.patch("sys.stdout")
    def test_lssteps_called(self, *args):
        with mock.patch("texttable.Texttable.header") as header, \
             mock.patch("texttable.Texttable.add_row") as row:
            cli.run_from_command_line()
            header.assert_called_with(
                ('Step Class', 'Process', 'Groups'))
            self.assertEquals(row.call_count, len(run.load_steps()))

    @mock.patch("sys.argv", new=["test", "lssteps"])
    @mock.patch("corral.core.setup_environment")
    @mock.patch("sys.stdout")
    def test_lssteps_none(self, *args):
        with mock.patch("corral.run.load_steps",
                        return_value=()) as load_steps:
            with mock.patch("texttable.Texttable.add_rows") as add_rows:
                cli.run_from_command_line()
                add_rows.assert_not_called()
                self.assertTrue(load_steps.called)


class LSAlerts(BaseTest):

    @mock.patch("sys.argv", new=["test", "lsalerts"])
    @mock.patch("corral.core.setup_environment")
    @mock.patch("sys.stdout")
    def test_lsalerts_called(self, *args):
        with mock.patch("texttable.Texttable.header") as header, \
             mock.patch("texttable.Texttable.add_row") as row:
            cli.run_from_command_line()
            header.assert_called_with(
                ('Alert Class', 'Process', 'Groups'))
            self.assertEquals(row.call_count, len(run.load_alerts()))

    @mock.patch("sys.argv", new=["test", "lsalerts"])
    @mock.patch("corral.core.setup_environment")
    @mock.patch("sys.stdout")
    def test_lsalerts_none(self, *args):
        with mock.patch("corral.run.load_alerts",
                        return_value=()) as load_alerts:
            with mock.patch("texttable.Texttable.add_rows") as add_rows:
                cli.run_from_command_line()
                add_rows.assert_not_called()
                self.assertTrue(load_alerts.called)


class Run(BaseTest):

    @mock.patch("sys.argv", new=["test", "run", "--sync"])
    @mock.patch("corral.core.setup_environment")
    def test_run_all(self, *args):
        with mock.patch(
            "corral.run.execute_step", return_value=[]
        ) as execute_step:
            cli.run_from_command_line()
            expected = map(lambda s: mock.call(s, sync=True), run.load_steps())
            execute_step.assert_has_calls(expected)

    @mock.patch("sys.argv", new=["test", "run"])
    @mock.patch("corral.core.setup_environment")
    def test_run_all_async(self, *args):
        call_count = len(run.load_steps())
        with mock.patch("corral.run.step.StepRunner.start") as proc_start:
            with mock.patch("corral.run.step.StepRunner.join") as proc_join:
                with mock.patch("sys.exit") as sys_exit:
                    with mock.patch("corral.run.step.StepRunner.exitcode", 0):
                        cli.run_from_command_line()
                        self.assertEquals(proc_start.call_count, call_count)
                        self.assertEquals(proc_join.call_count, call_count)
                        sys_exit.assert_not_called()
        with mock.patch("corral.run.step.StepRunner.start") as proc_start:
            with mock.patch("corral.run.step.StepRunner.join") as proc_join:
                with mock.patch("sys.exit") as sys_exit:
                    with mock.patch("corral.run.step.StepRunner.exitcode", 1):
                        cli.run_from_command_line()
                        self.assertEquals(proc_start.call_count, call_count)
                        self.assertEquals(proc_join.call_count, call_count)
                        sys_exit.assert_called_with(call_count)

    @mock.patch("sys.argv",
                new=["test", "run", "--steps", "Step1", "Step2", "--sync"])
    @mock.patch("corral.core.setup_environment")
    def test_run_explicit(self, *args):
        with mock.patch(
            "corral.run.execute_step", return_value=[]
        ) as execute_step:
            cli.run_from_command_line()
            expected = map(lambda s: mock.call(s, sync=True), run.load_steps())
            execute_step.assert_has_calls(expected)

    @mock.patch("sys.argv", new=["test", "run", "--steps", "Step1", "--sync"])
    @mock.patch("corral.core.setup_environment")
    def test_run_first(self, *args):
        with mock.patch("corral.run.execute_step") as execute_step:
            cli.run_from_command_line()
            expected = [mock.call(Step1, sync=True)]
            execute_step.assert_has_calls(expected)

    @mock.patch("sys.argv", new=["test", "run", "--steps", "Step2", "--sync"])
    @mock.patch("corral.core.setup_environment")
    def test_run_second(self, *args):
        with mock.patch("corral.run.execute_step") as execute_step:
            cli.run_from_command_line()
            expected = [mock.call(Step2, sync=True)]
            execute_step.assert_has_calls(expected)

    @mock.patch("sys.argv",
                new=["test", "run", "--steps", "Step2", "Step2", "--sync"])
    @mock.patch("corral.core.setup_environment")
    @mock.patch("sys.stderr")
    @mock.patch("sys.stdout")
    def test_run_duplicated(self, *args):
        with mock.patch("corral.run.execute_step"):
            with self.assertRaises(SystemExit):
                cli.run_from_command_line()

    @mock.patch("sys.argv", new=["test", "run", "--steps", "FOO", "--sync"])
    @mock.patch("corral.core.setup_environment")
    @mock.patch("sys.stderr")
    @mock.patch("sys.stdout")
    def test_run_invalid_step(self, *args):
        with mock.patch("corral.run.execute_step"):
            with self.assertRaises(SystemExit):
                cli.run_from_command_line()


class CheckAlerts(BaseTest):

    @mock.patch("sys.argv", new=["test", "check-alerts", "--sync"])
    @mock.patch("corral.core.setup_environment")
    def test_check_alerts_all(self, *args):
        with mock.patch(
            "corral.run.execute_alert", return_value=[]
        ) as execute_step:
            cli.run_from_command_line()
            expected = map(
                lambda s: mock.call(s, sync=True), run.load_alerts())
            execute_step.assert_has_calls(expected)

    @mock.patch("sys.argv", new=["test", "check-alerts"])
    @mock.patch("corral.core.setup_environment")
    def test_check_alerts_all_async(self, *args):
        call_count = len(run.load_alerts())
        with mock.patch("corral.run.alert.AlertRunner.start") as proc_start:
            with mock.patch("corral.run.alert.AlertRunner.join") as proc_join:
                with mock.patch("corral.run.alert.AlertRunner.exitcode", 0):
                    with mock.patch("sys.exit") as sys_exit:
                        cli.run_from_command_line()
                        self.assertEquals(proc_start.call_count, call_count)
                        self.assertEquals(proc_join.call_count, call_count)
                        sys_exit.assert_not_called()
        with mock.patch("corral.run.alert.AlertRunner.start") as proc_start:
            with mock.patch("corral.run.alert.AlertRunner.join") as proc_join:
                with mock.patch("corral.run.alert.AlertRunner.exitcode", 1):
                    with mock.patch("sys.exit") as sys_exit:
                        cli.run_from_command_line()
                        self.assertEquals(proc_start.call_count, call_count)
                        self.assertEquals(proc_join.call_count, call_count)
                        sys_exit.assert_called_once_with(call_count)

    @mock.patch("sys.argv",
                new=["test", "check-alerts", "--alerts", "Alert1", "--sync"])
    @mock.patch("corral.core.setup_environment")
    def test_check_alerts_explicit(self, *args):
        with mock.patch(
            "corral.run.execute_alert", return_value=[]
        ) as execute_alert:
            cli.run_from_command_line()
            expected = map(
                lambda s: mock.call(s, sync=True), run.load_alerts())
            execute_alert.assert_has_calls(expected)

    @mock.patch(
        "sys.argv",
        new=["test", "check-alerts", "--alerts", "Alert1", "Alert1", "--sync"]
    )
    @mock.patch("corral.core.setup_environment")
    @mock.patch("sys.stderr")
    @mock.patch("sys.stdout")
    def test_check_alerts_duplicated(self, *args):
        with mock.patch("corral.run.execute_alert"):
            with self.assertRaises(SystemExit):
                cli.run_from_command_line()

    @mock.patch(
        "sys.argv", new=["test", "check-alerts", "--alerts", "Foo", "--sync"])
    @mock.patch("corral.core.setup_environment")
    @mock.patch("sys.stderr")
    @mock.patch("sys.stdout")
    def test_check_alerts_invalid(self, *args):
        with mock.patch("corral.run.execute_alert"):
            with self.assertRaises(SystemExit):
                cli.run_from_command_line()


class CreateDoc(BaseTest):

    @mock.patch("corral.docs.create_doc", return_value="foo")
    @mock.patch("sys.argv", new=["test", "create-doc"])
    @mock.patch("corral.core.setup_environment")
    @mock.patch("sys.stdout")
    def test_create_doc_stdout(self, stdout, *args):
        cli.run_from_command_line()
        stdout.write.assert_any_call("foo")

    @mock.patch("corral.docs.create_doc", return_value="foo")
    @mock.patch("corral.core.setup_environment")
    @mock.patch("sys.stdout")
    def test_create_doc_file(self, stdout, *args):
        tempfile = self.get_tempfile()
        params = ["test", "create-doc", "-o", tempfile]
        with mock.patch("sys.argv", new=params):
            cli.run_from_command_line()
            self.assertEquals(open(tempfile).read(), "foo")


class CreateModelsDiagram(BaseTest):

    @mock.patch("corral.docs.models_diagram", return_value="foo")
    @mock.patch("sys.argv", new=["test", "create-models-diagram"])
    @mock.patch("corral.core.setup_environment")
    @mock.patch("sys.stdout")
    def test_create_md_stdout(self, stdout, *args):
        cli.run_from_command_line()
        stdout.write.assert_any_call("foo")

    @mock.patch("corral.docs.models_diagram", return_value="foo")
    @mock.patch("corral.core.setup_environment")
    @mock.patch("sys.stdout")
    def test_create_md_file(self, stdout, *args):
        tempfile = self.get_tempfile()
        params = ["test", "create-models-diagram", "-o", tempfile]
        with mock.patch("sys.argv", new=params):
            cli.run_from_command_line()
            self.assertEquals(open(tempfile).read(), "foo")


class QAReport(BaseTest):

    @mock.patch("corral.qa.qa_report")
    @mock.patch("corral.docs.qa_report", return_value="foo")
    @mock.patch("sys.argv", new=["test", "qareport"])
    @mock.patch("corral.core.setup_environment")
    @mock.patch("sys.stdout")
    def test_create_qar_stdout(self, stdout, *args):
        cli.run_from_command_line()
        stdout.write.assert_any_call("foo")

    @mock.patch("corral.qa.qa_report")
    @mock.patch("corral.docs.qa_report", return_value="foo")
    @mock.patch("corral.core.setup_environment")
    @mock.patch("sys.stdout")
    def test_create_qar_file(self, stdout, *args):
        tempfile = self.get_tempfile()
        params = ["test", "qareport", "-o", tempfile]
        with mock.patch("sys.argv", new=params):
            cli.run_from_command_line()
            self.assertEquals(open(tempfile).read(), "foo")


class Test(BaseTest):

    @mock.patch("sys.argv", new=["test", "test"])
    @mock.patch("corral.core.setup_environment")
    @mock.patch("sys.stdout")
    def test_test_all(self, *args):
        with mock.patch("corral.docs.qa.run_tests") as rt:
            cli.run_from_command_line()
            rt.assert_called()

    @mock.patch("sys.argv", new=["test", "test"])
    @mock.patch("corral.core.setup_environment")
    @mock.patch("sys.stdout")
    @mock.patch("sys.exit")
    def test_test_fail(self, sys_exit, *args):
        fresult = mock.MagicMock()
        with mock.patch.object(fresult, "wasSuccessful") as ws:
            ws.return_value = False
            with mock.patch("corral.docs.qa.run_tests", return_value=fresult):
                cli.run_from_command_line()
        sys_exit.assert_called_with(1)

    @mock.patch("corral.core.setup_environment")
    @mock.patch("sys.stdout")
    @mock.patch("sys.stderr")
    def test_test_by_name(self, *args):
        params = ["test", "test", "-s", "Step1",
                  "-a", "Alert1", "-c", "TestAPICommand"]
        expected = (
            [TestLoader, Step1, Alert1],
            [commands.TestAPICommand], False, 0, False)
        with mock.patch("sys.argv", new=params), \
                mock.patch("corral.docs.qa.run_tests") as rt:
                    cli.run_from_command_line()
                    rt.assert_called_with(*expected)

    @mock.patch("corral.core.setup_environment")
    @mock.patch("sys.stdout")
    @mock.patch("sys.stderr")
    def test_test_duplicated(self, *args):
        params = ["test", "test", "-s", "Step1", "Step1",
                  "-a", "Alert1", "-c", "TestAPICommand"]
        with mock.patch("sys.argv", new=params), \
                mock.patch("sys.exit") as sys_exit:
                    cli.run_from_command_line()
                    sys_exit.assert_called_with(1)
        params = ["test", "test", "-s", "Step1",
                  "-a", "Alert1", "Alert1", "-c", "TestAPICommand"]
        with mock.patch("sys.argv", new=params), \
                mock.patch("sys.exit") as sys_exit:
                    cli.run_from_command_line()
                    sys_exit.assert_called_with(1)
        params = ["test", "test", "-s", "Step1", "Step1",
                  "-a", "Alert1", "-c", "TestAPICommand"]
        with mock.patch("sys.argv", new=params), \
                mock.patch("sys.exit") as sys_exit:
                    cli.run_from_command_line()
                    sys_exit.assert_called_with(1)
        params = ["test", "test", "-s", "Step1",
                  "-a", "Alert1", "-c", "TestAPICommand", "TestAPICommand"]
        with mock.patch("sys.argv", new=params), \
                mock.patch("sys.exit") as sys_exit:
                    cli.run_from_command_line()
                    sys_exit.assert_called_with(1)

    @mock.patch("corral.core.setup_environment")
    @mock.patch("sys.stdout")
    @mock.patch("sys.stderr")
    def test_test_invalid_name(self, *args):
        params = ["test", "test", "-s", "Step1x",
                  "-a", "Alert1", "-c", "TestAPICommand"]
        with mock.patch("sys.argv", new=params), \
                mock.patch("sys.exit") as sys_exit:
                    cli.run_from_command_line()
                    sys_exit.assert_called_with(1)
        params = ["test", "test", "-s", "Step1",
                  "-a", "Alert1x", "-c", "TestAPICommand"]
        with mock.patch("sys.argv", new=params), \
                mock.patch("sys.exit") as sys_exit:
                    cli.run_from_command_line()
                    sys_exit.assert_called_with(1)
        params = ["test", "test", "-s", "Step1",
                  "-a", "Alert1", "-c", "TestAPICommandx"]
        with mock.patch("sys.argv", new=params), \
                mock.patch("sys.exit") as sys_exit:
                    cli.run_from_command_line()
                    sys_exit.assert_called_with(1)


class RunAll(BaseTest):

    @mock.patch("corral.core.setup_environment")
    @mock.patch("sys.stdout")
    @mock.patch("sys.stderr")
    @mock.patch("sys.argv", new=["test", "run-all"])
    def test_run_all(self, *args):
        with mock.patch("corral.run.execute_loader") as execute_loader, \
                mock.patch("corral.run.execute_step") as execute_step, \
                mock.patch("corral.run.execute_alert") as execute_alert:
                    cli.run_from_command_line()
                    execute_loader.assert_any_call(TestLoader)
                    execute_step.assert_any_call(Step1)
                    execute_step.assert_any_call(Step2)
                    execute_alert.assert_any_call(Alert1)

    @mock.patch("sys.argv", new=["test", "run-all"])
    @mock.patch("corral.core.setup_environment")
    @mock.patch("sys.stdout")
    @mock.patch("sys.exit")
    def test_run_fail(self, sys_exit, *args):
        fproc = mock.MagicMock()
        fproc.exitcode = 1
        with mock.patch("corral.run.execute_loader", return_value=[fproc]), \
                mock.patch("corral.run.execute_step"), \
                mock.patch("corral.run.execute_alert"):
                    cli.run_from_command_line()
        sys_exit.assert_called_with(1)
