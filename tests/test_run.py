#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# DOC
# =============================================================================

"""All Corral base tests"""


# =============================================================================
# IMPORTS
# =============================================================================

from corral import run, exceptions, db

import mock

from .steps import TestLoader, Step1, Step2
from .models import SampleModel

from .base import BaseTest


# =============================================================================
# BASE CLASS
# =============================================================================

class TestLoaderFunctions(BaseTest):

    def test_load_loader(self):
        actual = run.load_loader()
        self.assertIs(actual, TestLoader)

        with mock.patch("corral.conf.settings.LOADER", new="os.open"):
            with self.assertRaises(exceptions.ImproperlyConfigured):
                run.load_loader()

    def test_execute_no_loader(self):
        with self.assertRaises(TypeError):
            run.execute_loader("foo")

    def test_execute_loader(self):
        run.execute_loader(TestLoader)
        with db.session_scope() as session:
            self.assertEqual(session.query(SampleModel).count(), 1)

        with mock.patch("tests.steps.TestLoader.generate",
                        return_value=[None]):
                with self.assertRaises(TypeError):
                    run.execute_loader(TestLoader)


class TestExecuteFunction(BaseTest):

    def test_load_steps(self):
        actual = run.load_steps()
        expected = (Step1, Step2)
        self.assertEqual(actual, expected)

        with mock.patch("corral.conf.settings.STEPS", new=["os.open"]):
            with self.assertRaises(exceptions.ImproperlyConfigured):
                run.load_steps()

    def test_step_return_no_model(self):
        with mock.patch("tests.steps.Step1.generate", return_value=[None]):
            with self.assertRaises(TypeError):
                run.execute_step(Step1)

    def test_execute_no_setp(self):
        with self.assertRaises(TypeError):
            run.execute_step("foo")

    def test_execute_step(self):
        sample_id = None
        with db.session_scope() as session:
            sample = SampleModel(name=None)
            session.add(sample)
            session.commit()
            sample_id = sample.id

        run.execute_step(Step1)
        with db.session_scope() as session:
            query = session.query(SampleModel)
            self.assertEqual(query.count(), 1)
            sample = session.query(SampleModel).get(sample_id)
            self.assertEqual(sample.name, "Step1")

        run.execute_step(Step2)
        with db.session_scope() as session:
            query = session.query(SampleModel)
            self.assertEqual(query.count(), 2)
            sample = session.query(SampleModel).get(sample_id)
            self.assertEqual(sample.name, "Step2")

        run.execute_step(Step1)
        with db.session_scope() as session:
            query = session.query(SampleModel)
            self.assertEqual(query.count(), 2)
            sample = session.query(SampleModel).get(sample_id)
            self.assertEqual(sample.name, "Step2")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)
