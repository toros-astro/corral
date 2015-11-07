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


class CreateDB(BaseTest):

    @mock.patch("sys.argv", new=["test", "createdb"])
    @mock.patch("corral.core.setup_environment")
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
                    ("Do you want to create the database[Yes/no]? ",
                     "Please answer 'yes' or 'no': ")]
                ask.assert_has_calls(expected)
                self.assertFalse(create_all.called)

    @mock.patch("sys.argv", new=["test", "createdb", "--noinput"])
    @mock.patch("corral.core.setup_environment")
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
            execute_loader.assert_called_with(TestLoader)


class Run(BaseTest):

    @mock.patch("sys.argv", new=["test", "run"])
    @mock.patch("corral.core.setup_environment")
    def test_run_all_command(self, *args):
        with mock.patch("corral.run.execute_step") as execute_step:
            cli.run_from_command_line()
            expected = map(mock.call, run.load_steps())
            execute_step.assert_has_calls(expected)

    @mock.patch("sys.argv", new=["test", "run", "--steps", "Step1", "Step2"])
    @mock.patch("corral.core.setup_environment")
    def test_run_explicit(self, *args):
        with mock.patch("corral.run.execute_step") as execute_step:
            cli.run_from_command_line()
            expected = map(mock.call, run.load_steps())
            execute_step.assert_has_calls(expected)

    @mock.patch("sys.argv", new=["test", "run", "--steps", "Step1"])
    @mock.patch("corral.core.setup_environment")
    def test_run_first(self, *args):
        with mock.patch("corral.run.execute_step") as execute_step:
            cli.run_from_command_line()
            expected = [mock.call(Step1)]
            execute_step.assert_has_calls(expected)

    @mock.patch("sys.argv", new=["test", "run", "--steps", "Step2"])
    @mock.patch("corral.core.setup_environment")
    def test_run_second(self, *args):
        with mock.patch("corral.run.execute_step") as execute_step:
            cli.run_from_command_line()
            expected = [mock.call(Step2)]
            execute_step.assert_has_calls(expected)

    @mock.patch("sys.argv", new=["test", "run", "--steps", "Step2", "Step2"])
    @mock.patch("corral.core.setup_environment")
    @mock.patch("sys.stderr")
    def test_run_duplicated(self, *args):
        with mock.patch("corral.run.execute_step"):
            with self.assertRaises(SystemExit):
                cli.run_from_command_line()

    @mock.patch("sys.argv", new=["test", "run", "--steps", "FOO"])
    @mock.patch("corral.core.setup_environment")
    @mock.patch("sys.stderr")
    def test_run_invalid_step(self, *args):
        with mock.patch("corral.run.execute_step"):
            with self.assertRaises(SystemExit):
                cli.run_from_command_line()
