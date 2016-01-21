#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# DOC
# =============================================================================

"""All settings tests"""


# =============================================================================
# IMPORTS
# =============================================================================

import os

import mock

from corral import cli, run, db, exceptions
from corral.cli import commands as builtin_commands

from . import commands
from .steps import TestLoader, Step1, Step2
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
    def test_stack_trace_option(self, *args):
        with mock.patch("sys.argv", new=["test",  "--stacktrace", "foo"]):
            with self.assertRaises(Exception):
                cli.run_from_command_line()
        with mock.patch("sys.argv", new=["test", "foo"]):
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
    def test_notebook_command(self, *args):
        with mock.patch("IPython.start_ipython") as start_ipython:
            cli.run_from_command_line()
            self.assertTrue(start_ipython.called)
            expected = [mock.call(argv=['notebook'])]
            start_ipython.assert_has_calls(expected)


class Load(BaseTest):

    @mock.patch("sys.argv", new=["test", "load"])
    @mock.patch("corral.core.setup_environment")
    def test_load(self, *args):
        with mock.patch("corral.run.execute_loader") as execute_loader:
            cli.run_from_command_line()
            execute_loader.assert_called_with(TestLoader, sync=True)


class LSSteps(BaseTest):

    @mock.patch("sys.argv", new=["test", "lssteps"])
    @mock.patch("corral.core.setup_environment")
    @mock.patch("sys.stdout")
    def test_lssteps(self, *args):
        with mock.patch("corral.run.load_steps") as load_steps:
            with mock.patch("texttable.Texttable.header") as header:
                cli.run_from_command_line()
                header.assert_called_with(
                    ('Step Class', 'Process', 'Groups'))
                self.assertTrue(load_steps.called)

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
    def test_run_duplicated(self, *args):
        with mock.patch("corral.run.execute_step"):
            with self.assertRaises(SystemExit):
                cli.run_from_command_line()

    @mock.patch("sys.argv", new=["test", "run", "--steps", "FOO", "--sync"])
    @mock.patch("corral.core.setup_environment")
    @mock.patch("sys.stderr")
    def test_run_invalid_step(self, *args):
        with mock.patch("corral.run.execute_step"):
            with self.assertRaises(SystemExit):
                cli.run_from_command_line()


class LSAlerts(BaseTest):

    @mock.patch("sys.argv", new=["test", "lsalerts"])
    @mock.patch("corral.core.setup_environment")
    @mock.patch("sys.stdout")
    def test_lsalerts(self, *args):
        with mock.patch("corral.run.load_alerts") as load_alerts:
            with mock.patch("texttable.Texttable.header") as header:
                cli.run_from_command_line()
                header.assert_called_with(
                    ('Alert Class', 'Process', 'Groups'))
                self.assertTrue(load_alerts.called)

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
    def test_check_alerts_duplicated(self, *args):
        with mock.patch("corral.run.execute_alert"):
            with self.assertRaises(SystemExit):
                cli.run_from_command_line()

    @mock.patch(
        "sys.argv", new=["test", "check-alerts", "--alerts", "Foo", "--sync"])
    @mock.patch("corral.core.setup_environment")
    @mock.patch("sys.stderr")
    def test_check_alerts_invalid(self, *args):
        with mock.patch("corral.run.execute_alert"):
            with self.assertRaises(SystemExit):
                cli.run_from_command_line()
