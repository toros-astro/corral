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
