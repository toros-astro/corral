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
from corral.db.default_models import Alerted

import mock

from .steps import TestLoader, Step1, Step2
from .alerts import Alert1
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
            run.execute_loader("foo", sync=True)

    def test_execute_loader(self):
        run.execute_loader(TestLoader, sync=True)
        with db.session_scope() as session:
            self.assertEqual(session.query(SampleModel).count(), 1)
        with mock.patch("tests.steps.TestLoader.generate",
                        return_value=[None]):
                with self.assertRaises(TypeError):
                    run.execute_loader(TestLoader, sync=True)


class TestStepFunctions(BaseTest):

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
                run.execute_step(Step1, sync=True)

    def test_execute_no_step(self):
        with self.assertRaises(TypeError):
            run.execute_step("foo", sync=True)

    def test_execute_step(self):
        sample_id = None
        with db.session_scope() as session:
            sample = SampleModel(name=None)
            session.add(sample)
            session.commit()
            sample_id = sample.id

        run.execute_step(Step1, sync=True)
        with db.session_scope() as session:
            query = session.query(SampleModel)
            self.assertEqual(query.count(), 1)
            sample = session.query(SampleModel).get(sample_id)
            self.assertEqual(sample.name, "Step1")

        run.execute_step(Step2, sync=True)
        with db.session_scope() as session:
            query = session.query(SampleModel)
            self.assertEqual(query.count(), 2)
            sample = session.query(SampleModel).get(sample_id)
            self.assertEqual(sample.name, "Step2")

        run.execute_step(Step1, sync=True)
        with db.session_scope() as session:
            query = session.query(SampleModel)
            self.assertEqual(query.count(), 2)
            sample = session.query(SampleModel).get(sample_id)
            self.assertEqual(sample.name, "Step2")

    def test_default_generate_without_model_or_conditions(self):
        with mock.patch("tests.steps.Step1.model", None):
            with self.assertRaises(NotImplementedError):
                run.execute_step(Step1, sync=True)
        with mock.patch("tests.steps.Step1.conditions", None):
            with self.assertRaises(NotImplementedError):
                run.execute_step(Step1, sync=True)

    @mock.patch("corral.run.step.StepRunner.start")
    @mock.patch("corral.run.step.StepRunner.join")
    def test_procces_corectly_created(self, *args):
        with mock.patch("tests.steps.Step1.procno", 20):
            procs = run.execute_step(Step1)
            self.assertEqual(len(procs), 20)


class TestAlertFunctions(BaseTest):

    def test_load_alerts(self):
        actual = run.load_alerts()
        expected = (Alert1,)
        self.assertEqual(actual, expected)

        with mock.patch("corral.conf.settings.ALERTS", new=["os.open"]):
            with self.assertRaises(exceptions.ImproperlyConfigured):
                run.load_alerts()

    def test_alert_return_no_model(self):
        with mock.patch("tests.alerts.Alert1.generate", return_value=[None]):
            with self.assertRaises(TypeError):
                run.execute_alert(Step1, sync=True)

    def test_execute_no_alert(self):
        with self.assertRaises(TypeError):
            run.execute_alert("foo", sync=True)

    def test_execute_step(self):
        alert_to = Alert1.alert_to[0]

        sample_id = None
        with db.session_scope() as session:
            sample = SampleModel(name="catch_alert")
            session.add(sample)
            session.commit()
            sample_id = sample.id

        run.execute_alert(Alert1, sync=True)
        self.assertEquals(alert_to.fp.getvalue(), "catch_alert")
        with db.session_scope() as session:
            query = session.query(Alerted)
            self.assertEqual(query.count(), 1)
            alerted = query.first()
            sample = session.query(SampleModel).get(sample_id)
            self.assertEquals(alerted.model, sample)

        run.execute_alert(Alert1, sync=True)
        with db.session_scope() as session:
            query = session.query(Alerted)
            self.assertEqual(query.count(), 1)
            alerted = query.first()
            sample = session.query(SampleModel).get(sample_id)
            self.assertEquals(alerted.model, sample)

    @mock.patch("corral.run.alert.AlertRunner.start")
    @mock.patch("corral.run.alert.AlertRunner.join")
    def test_procces_corectly_created(self, *args):
        with mock.patch("tests.alerts.Alert1.procno", 20):
            procs = run.execute_alert(Alert1)
            self.assertEqual(len(procs), 20)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)
