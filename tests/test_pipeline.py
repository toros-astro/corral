#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# DOC
# =============================================================================

"""All settings tests"""


# =============================================================================
# IMPORTS
# =============================================================================

import mock

from corral import setup, exceptions

from .base import BaseTest
from .pipeline import TestPipeline


# =============================================================================
# BASE CLASS
# =============================================================================

class LoadSetupTests(BaseTest):

    def test_load_setup(self):
        actual = setup.load_pipeline_setup()
        self.assertIs(actual, TestPipeline)

    def test_always_the_same(self):
        self.assertIs(TestPipeline(), TestPipeline())
        self.assertIs(TestPipeline(), setup.load_pipeline_setup()())
        self.assertIs(setup.load_pipeline_setup()(),
                      setup.load_pipeline_setup()())

    def test_load_setup_fail(self):
        with mock.patch("corral.conf.settings.PIPELINE_SETUP", new="os.open"):
            with self.assertRaises(exceptions.ImproperlyConfigured):
                setup.load_pipeline_setup()


class SetupTests(BaseTest):

    def test_setup_pipeline(self):
        with mock.patch("atexit.register") as register:
            with mock.patch.object(TestPipeline, "setup") as pipeline_setup:
                setup.setup_pipeline(TestPipeline)
                self.assertTrue(pipeline_setup.called)
                register.assert_called_with(TestPipeline().teardown)

    def test_setup_pipeline_fail(self):
        with self.assertRaises(TypeError):
            setup.setup_pipeline(None)


