#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# DOC
# =============================================================================

"""All settings tests"""


# =============================================================================
# IMPORTS
# =============================================================================

import argparse
import os

import mock

import six

from corral import cli, run, db, exceptions
from corral.cli import commands as builtin_commands

from . import commands
from .steps import TestLoader, Step1, Step2
from .base import BaseTest


# =============================================================================
# BASE CLASS
# =============================================================================

class TestCli(BaseTest):

    def test_command_ask(self):
        with mock.patch("six.moves.input") as sinput:
            cmd = commands.TestAPICommand(mock.Mock())
            cmd.setup()
            cmd.ask("foo")
            sinput.assert_called_once_with("foo")

    def test_load_commands_module(self):
        actual = cli.load_commands_module()
        self.assertIs(actual, commands)

        with mock.patch("sys.stderr", new_callable=six.StringIO):
            with mock.patch("corral.util.dimport", side_effect=ImportError()):
                actual = cli.load_commands_module()
                self.assertIsNone(actual)

        with mock.patch("sys.stderr", new_callable=six.StringIO):
            with mock.patch("corral.util.dimport", side_effect=Exception()):
                with self.assertRaises(Exception):
                    cli.load_commands_module()

    def test_duplicate_title(self):
        patch = "tests.commands.TestAPICommand.options"
        with mock.patch.dict(patch, {"title": "exec"}):
            with mock.patch("corral.core.setup_environment"):
                with self.assertRaises(exceptions.ImproperlyConfigured):
                    cli.run_from_command_line([])

    def test_command_api(self):
        with mock.patch("corral.core.setup_environment") as setup_environment:
            with mock.patch("tests.commands.TestAPICommand.setup") as setup:
                with mock.patch("tests.commands.TestAPICommand.handle") as hdl:
                    cli.run_from_command_line(["foo"])
                    self.assertTrue(setup_environment.called)
                    self.assertTrue(setup.called)
                    self.assertTrue(hdl.called)

    def test_extract_func(self):
        ns = argparse.Namespace(func="func", foo="foo", faa="faa")

        actual = cli.extract_func(ns)
        expected = ("func", {"foo": "foo", "faa": "faa"})
        self.assertEqual(actual, expected)


class CreateDB(BaseTest):

    def test_create_db_comand(self):
        patch = "corral.cli.commands.CreateDB.ask"
        with mock.patch(patch, return_value="yes") as ask:
            with mock.patch("corral.db.create_all") as create_all:
                with mock.patch("corral.core.setup_environment"):
                    cli.run_from_command_line(["createdb"])
                    self.assertTrue(ask.called)
                    self.assertTrue(create_all.called)

        with mock.patch(patch, return_value="no") as ask:
            with mock.patch("corral.db.create_all") as create_all:
                with mock.patch("corral.core.setup_environment"):
                    cli.run_from_command_line(["createdb"])
                    self.assertTrue(ask.called)
                    create_all.assert_not_called()

        with mock.patch(patch, return_value="yes") as ask:
            with mock.patch("corral.db.create_all") as create_all:
                with mock.patch("corral.core.setup_environment"):
                    cli.run_from_command_line(["createdb", "--noinput"])
                    ask.assert_not_called()
                    self.assertTrue(create_all.called)

        with mock.patch(patch, return_value="no") as ask:
            with mock.patch("corral.db.create_all") as create_all:
                with mock.patch("corral.core.setup_environment"):
                    cli.run_from_command_line(["createdb", "--noinput"])
                    ask.assert_not_called()
                    self.assertTrue(create_all.called)

        with mock.patch(patch, side_effect=["foo", "no"]) as ask:
            with mock.patch("corral.db.create_all") as create_all:
                with mock.patch("corral.core.setup_environment"):
                    cli.run_from_command_line(["createdb"])
                    expected = [
                        mock.call(arg) for arg in
                        ("Do you want to create the database[Yes/no]? ",
                         "Please answer 'yes' or 'no': ")]
                    ask.assert_has_calls(expected)
                    self.assertFalse(create_all.called)


class Shell(BaseTest):

    def test_default_shell_command(self):
        mockeable_shell_calls = {
            "ipython": "IPython.start_ipython",
            "bpython": "bpython.embed",
            "plain": "code.InteractiveConsole.interact",
        }

        shell_cmd = builtin_commands.Shell(mock.Mock())
        shell_cmd.setup()
        shells = shell_cmd.shells

        first_shell = tuple(shells.keys())[0]
        to_mock = mockeable_shell_calls[first_shell]

        with mock.patch(to_mock) as call:
            with mock.patch("corral.core.setup_environment"):
                cli.run_from_command_line(["shell"])
                self.assertTrue(call.called)

    def test_ipython(self):
        with mock.patch("IPython.start_ipython") as start_ipython:
            with mock.patch("corral.core.setup_environment"):
                cli.run_from_command_line(["shell", "--shell", "ipython"])
                self.assertTrue(start_ipython.called)

    def test_bpython(self):
        with mock.patch("bpython.embed") as embed:
            with mock.patch("corral.core.setup_environment"):
                cli.run_from_command_line(["shell", "--shell", "bpython"])
                self.assertTrue(embed.called)

    def test_plain(self):
        with mock.patch("code.InteractiveConsole.interact") as interact:
            with mock.patch("corral.core.setup_environment"):
                cli.run_from_command_line(["shell", "--shell", "plain"])
                self.assertTrue(interact.called)


class DBShell(BaseTest):

    def test_dbshell(self):
        with mock.patch("corral.libs.sqlalchemy_sql_shell.run") as run_dbshell:
            with mock.patch("corral.core.setup_environment"):
                with mock.patch("sys.stdout"):
                    cli.run_from_command_line(["dbshell"])
                    run_dbshell.assert_called_with(db.engine)


class Exec(BaseTest):

    def test_execfile(self):
        path = os.path.abspath(os.path.dirname(__file__))
        script = os.path.join(path, "script.py")
        with mock.patch("corral.core.setup_environment"):
            cli.run_from_command_line(["exec", script])


class Notebook(BaseTest):

    def test_notebook_command(self):
        with mock.patch("IPython.start_ipython") as start_ipython:
            with mock.patch("corral.core.setup_environment"):
                cli.run_from_command_line(["notebook"])
                self.assertTrue(start_ipython.called)
                expected = [mock.call(argv=['notebook'])]
                start_ipython.assert_has_calls(expected)


class Load(BaseTest):

    def test_load(self):
        with mock.patch("corral.run.execute_loader") as execute_loader:
            with mock.patch("corral.core.setup_environment"):
                cli.run_from_command_line(["load"])
                execute_loader.assert_called_with(TestLoader)


class Run(BaseTest):

    def test_run_all_command(self):
        with mock.patch("corral.run.execute_step") as execute_step:
            with mock.patch("corral.core.setup_environment"):
                cli.run_from_command_line(["run"])
                expected = map(mock.call, run.load_steps())
                execute_step.assert_has_calls(expected)

    def test_run_explicit(self):
        with mock.patch("corral.run.execute_step") as execute_step:
            with mock.patch("corral.core.setup_environment"):
                cli.run_from_command_line(["run", "--steps", "Step1", "Step2"])
                expected = map(mock.call, run.load_steps())
                execute_step.assert_has_calls(expected)

    def test_run_first(self):
        with mock.patch("corral.run.execute_step") as execute_step:
            with mock.patch("corral.core.setup_environment"):
                cli.run_from_command_line(["run", "--steps", "Step1"])
                expected = [mock.call(Step1)]
                execute_step.assert_has_calls(expected)

    def test_run_second(self):
        with mock.patch("corral.run.execute_step") as execute_step:
            with mock.patch("corral.core.setup_environment"):
                cli.run_from_command_line(["run", "--steps", "Step2"])
                expected = [mock.call(Step2)]
                execute_step.assert_has_calls(expected)

    def test_run_duplicated(self):
        with mock.patch("corral.run.execute_step"):
            with mock.patch("sys.stderr"):
                with mock.patch("corral.core.setup_environment"):
                    with self.assertRaises(SystemExit):
                        cli.run_from_command_line(
                            ["run", "--steps", "Step2", "Step2"])

    def test_run_invalid_step(self):
        with mock.patch("corral.run.execute_step"):
            with mock.patch("sys.stderr"):
                with mock.patch("corral.core.setup_environment"):
                    with self.assertRaises(SystemExit):
                        cli.run_from_command_line(
                            ["run", "--steps", "FOO"])


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)
