#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# DOC
# =============================================================================

"""All settings tests"""


# =============================================================================
# IMPORTS
# =============================================================================

from corral import noenvcli

import mock

from .base import BaseTest


# =============================================================================
# BASE CLASS
# =============================================================================

class Create(BaseTest):

    @mock.patch("sys.argv", new=["test", "create", "foo"])
    @mock.patch("corral.creator.create_pipeline")
    def test_create_comand(self, create_pipeline):
        noenvcli.run_from_command_line()
        create_pipeline.assert_called_with(path="foo")

    @mock.patch("corral.creator.create_pipeline", side_effect=Exception)
    @mock.patch("sys.stderr")
    def test_stack_trace_option(self, *args):
        with mock.patch("sys.argv",
                        new=["test", "--stacktrace", "create", "foo"]):
            with self.assertRaises(Exception):
                noenvcli.run_from_command_line()
        with mock.patch("sys.argv", new=["test", "create", "foo"]):
            noenvcli.run_from_command_line()
