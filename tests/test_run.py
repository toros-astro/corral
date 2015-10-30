#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# DOC
# =============================================================================

"""All Corral base tests"""


# =============================================================================
# IMPORTS
# =============================================================================

from corral import run, conf, exceptions, db

import mock

from .steps import TestLoader, Step1, Step2
from .models import SampleModel

from .base import BaseTest


# =============================================================================
# BASE CLASS
# =============================================================================

class TestSteps(BaseTest):

    def test_load_loader(self):
        actual = run.load_loader()
        self.assertIs(actual, TestLoader)

        with mock.patch("corral.conf.settings.LOADER", new="os.open"):
            with self.assertRaises(exceptions.ImproperlyConfigured):
                run.load_loader()

    def test_load_steps(self):
        actual = run.load_steps()
        expected = (Step1, Step2)
        self.assertEqual(actual, expected)

        with mock.patch("corral.conf.settings.STEPS", new=["os.open"]):
            with self.assertRaises(exceptions.ImproperlyConfigured):
                run.load_steps()

    def test_execute_loader(self):
        run.execute_loader(TestLoader)
        with db.session_scope() as session:
            self.assertTrue(session.query(SampleModel).count(), 1)

        with mock.patch(
            "tests.steps.TestLoader.generate", return_value=[None]):
                with self.assertRaises(TypeError):
                    run.execute_loader(TestLoader)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)
