#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# DOC
# =============================================================================

"""All settings tests"""


# =============================================================================
# IMPORTS
# =============================================================================

import sys
import inspect
import argparse
import random

import mock

from corral import cli, core

from .cli import TestAPICommand
from .base import BaseTest

# =============================================================================
# BASE CLASS
# =============================================================================

class TestCli(BaseTest):

    def test_command_api(self):

        actual = {}
        seed = random.random()

        TestAPICommand.set_ns(actual, seed)

        with mock.patch("corral.core.setup_environment") as setup_environment:
            cli.run_from_command_line(["foo"])
            self.assertTrue(setup_environment.called)

        self.assertEqual(
            actual,
            {'setup': seed, 'add_arguments': seed + 1, 'handle': seed + 2})

    def test_extract_func(self):
        ns = argparse.Namespace(func="func", foo="foo", faa="faa")

        actual = cli.extract_func(ns)
        expected = ("func", {"foo": "foo", "faa": "faa"})
        self.assertEqual(actual, expected)

    def test_create_db_comand(self):
        with mock.patch("corral.cli.CreateDB.ask", return_value="yes") as ask:
            with mock.patch("corral.db.create_all") as create_all:
                with mock.patch("corral.core.setup_environment"):
                    cli.run_from_command_line(["createdb"])
                    self.assertTrue(ask.called)
                    self.assertTrue(create_all.called)

        with mock.patch("corral.cli.CreateDB.ask", return_value="no") as ask:
            with mock.patch("corral.db.create_all") as create_all:
                with mock.patch("corral.core.setup_environment"):
                    cli.run_from_command_line(["createdb"])
                    self.assertTrue(ask.called)
                    self.assertFalse(create_all.called)

        with mock.patch("corral.cli.CreateDB.ask", return_value="yes") as ask:
            with mock.patch("corral.db.create_all") as create_all:
                with mock.patch("corral.core.setup_environment"):
                    cli.run_from_command_line(["createdb", "--noinput"])
                    self.assertFalse(ask.called)
                    self.assertTrue(create_all.called)

        with mock.patch("corral.cli.CreateDB.ask", return_value="no") as ask:
            with mock.patch("corral.db.create_all") as create_all:
                with mock.patch("corral.core.setup_environment"):
                    cli.run_from_command_line(["createdb", "--noinput"])
                    self.assertFalse(ask.called)
                    self.assertTrue(create_all.called)

    def test_shell_command(self):
        mockeable_shell_calls = {
            "ipython": "IPython.start_ipython",
            "bpython": "bpython.embed",
            "plain": "code.InteractiveConsole.interact",
        }

        shell_cmd = cli.Shell()
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
                self.assertEqual(
                    start_ipython.call_args[1], {'argv': ['notebook']})


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)
