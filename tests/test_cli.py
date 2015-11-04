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
import random

import mock

from corral import cli, run
from corral.cli import commands as builtin_commands

from .commands import TestAPICommand
from .steps import TestLoader, Step1, Step2
from .base import BaseTest


# =============================================================================
# BASE CLASS
# =============================================================================

class TestCli(BaseTest):

    def test_command_api(self):

        with mock.patch("corral.core.setup_environment") as setup_environment:
            with mock.patch("tests.commands.TestAPICommand.setup") as setup:
                with mock.patch("tests.commands.TestAPICommand.handle") as hdl:
                    cli.run_from_command_line(["foo"])
                    setup_environment.assert_any_call()
                    setup.assert_any_call()
                    hdl.assert_any_call()

    def test_extract_func(self):
        ns = argparse.Namespace(func="func", foo="foo", faa="faa")

        actual = cli.extract_func(ns)
        expected = ("func", {"foo": "foo", "faa": "faa"})
        self.assertEqual(actual, expected)

    def test_create_db_comand(self):
        with mock.patch("corral.cli.commands.CreateDB.ask", return_value="yes") as ask:
            with mock.patch("corral.db.create_all") as create_all:
                with mock.patch("corral.core.setup_environment"):
                    cli.run_from_command_line(["createdb"])
                    self.assertTrue(ask.called)
                    self.assertTrue(create_all.called)

        with mock.patch("corral.cli.commands.CreateDB.ask", return_value="no") as ask:
            with mock.patch("corral.db.create_all") as create_all:
                with mock.patch("corral.core.setup_environment"):
                    cli.run_from_command_line(["createdb"])
                    self.assertTrue(ask.called)
                    create_all.assert_not_called()

        with mock.patch("corral.cli.commands.CreateDB.ask", return_value="yes") as ask:
            with mock.patch("corral.db.create_all") as create_all:
                with mock.patch("corral.core.setup_environment"):
                    cli.run_from_command_line(["createdb", "--noinput"])
                    ask.assert_not_called()
                    self.assertTrue(create_all.called)

        with mock.patch("corral.cli.commands.CreateDB.ask", return_value="no") as ask:
            with mock.patch("corral.db.create_all") as create_all:
                with mock.patch("corral.core.setup_environment"):
                    cli.run_from_command_line(["createdb", "--noinput"])
                    ask.assert_not_called()
                    self.assertTrue(create_all.called)

    def test_shell_command(self):
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

        with mock.patch("IPython.start_ipython") as start_ipython:
            with mock.patch("corral.core.setup_environment"):
                cli.run_from_command_line(["shell", "--shell", "ipython"])
                self.assertTrue(start_ipython.called)

        with mock.patch("bpython.embed") as embed:
            with mock.patch("corral.core.setup_environment"):
                cli.run_from_command_line(["shell", "--shell", "bpython"])
                self.assertTrue(embed.called)

        with mock.patch("code.InteractiveConsole.interact") as interact:
            with mock.patch("corral.core.setup_environment"):
                cli.run_from_command_line(["shell", "--shell", "plain"])
                self.assertTrue(interact.called)

    def test_notebook_command(self):
        with mock.patch("IPython.start_ipython") as start_ipython:
            with mock.patch("corral.core.setup_environment"):
                cli.run_from_command_line(["notebook"])
                self.assertTrue(start_ipython.called)
                expected = [mock.call(argv=['notebook'])]
                start_ipython.assert_has_calls(expected)

    def test_run_command(self):
        with mock.patch("corral.run.execute_step") as execute_step:
            with mock.patch("corral.core.setup_environment"):
                cli.run_from_command_line(["run"])
                expected = map(mock.call, run.load_steps())
                execute_step.assert_has_calls(expected)

        with mock.patch("corral.run.execute_step") as execute_step:
            with mock.patch("corral.core.setup_environment"):
                cli.run_from_command_line(["run", "--steps", "Step1", "Step2"])
                expected = map(mock.call, run.load_steps())
                execute_step.assert_has_calls(expected)

        with mock.patch("corral.run.execute_step") as execute_step:
            with mock.patch("corral.core.setup_environment"):
                cli.run_from_command_line(["run", "--steps", "Step1"])
                expected = [mock.call(Step1)]
                execute_step.assert_has_calls(expected)

        with mock.patch("corral.run.execute_step") as execute_step:
            with mock.patch("corral.core.setup_environment"):
                cli.run_from_command_line(["run", "--steps", "Step2"])
                expected = [mock.call(Step2)]
                execute_step.assert_has_calls(expected)

        with mock.patch("corral.run.execute_step") as execute_step:
            with mock.patch("sys.stderr"):
                with mock.patch("corral.core.setup_environment"):
                    with self.assertRaises(SystemExit):
                        cli.run_from_command_line(
                            ["run", "--steps", "Step2", "Step2"])

        with mock.patch("corral.run.execute_step") as execute_step:
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
