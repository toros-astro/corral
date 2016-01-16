#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# DOC
# =============================================================================

"""All Corral base tests"""


# =============================================================================
# IMPORTS
# =============================================================================

import tempfile
import os

from corral import run, exceptions, db, conf
from corral.db.default_models import Alerted
from corral.run import endpoints as ep

import mock

import six

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

    @mock.patch("corral.run.loader.LoaderRunner.start")
    @mock.patch("corral.run.loader.LoaderRunner.join")
    def test_procces_corectly_created(self, *args):
        with mock.patch("tests.steps.TestLoader.procno", 20):
            procs = run.execute_loader(TestLoader)
            self.assertEqual(len(procs), 20)


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

    def test_execute_alert(self):
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
            self.assertEquals(alerted.alert, Alert1)

        run.execute_alert(Alert1, sync=True)
        with db.session_scope() as session:
            query = session.query(Alerted)
            self.assertEqual(query.count(), 1)
            alerted = query.first()
            sample = session.query(SampleModel).get(sample_id)
            self.assertEquals(alerted.model, sample)
            self.assertEquals(alerted.alert, Alert1)

    def test_execute_alert_default_render(self):
        alert_to = Alert1.alert_to[0]

        with db.session_scope() as session:
            sample = SampleModel(name="catch_alert")
            session.add(sample)
            session.commit()

        expected = []

        def render(self, *args, **kwargs):
            rendered = super(Alert1, self).render_alert(*args, **kwargs)
            expected.append(rendered)
            return expected[-1]

        with mock.patch("tests.alerts.Alert1.render_alert", render):
            run.execute_alert(Alert1, sync=True)
        self.assertEquals(alert_to.fp.getvalue(), expected[-1])

    def test_alert_without_model_or_conditions(self):
        with mock.patch("tests.alerts.Alert1.model", None):
            with self.assertRaises(NotImplementedError):
                run.execute_alert(Alert1, sync=True)
        with mock.patch("tests.alerts.Alert1.model", None):
            with self.assertRaises(NotImplementedError):
                run.execute_alert(Alert1, sync=True)

    @mock.patch("corral.run.alert.AlertRunner.start")
    @mock.patch("corral.run.alert.AlertRunner.join")
    def test_procces_corectly_created(self, *args):
        with mock.patch("tests.alerts.Alert1.procno", 20):
            procs = run.execute_alert(Alert1)
            self.assertEqual(len(procs), 20)

    @mock.patch("tests.alerts.Alert1.auto_register", False)
    def test_manual_register_filter_registered(self):

        with db.session_scope() as session:
            sample = SampleModel(name="catch_alert")
            session.add(sample)
            session.commit()

        with self.assertRaises(NotImplementedError):
            run.execute_alert(Alert1, sync=True)

        with mock.patch("tests.alerts.Alert1.filter_registered") as flt_reg:
            run.execute_alert(Alert1, sync=True)
            with db.session_scope() as session:
                actual = flt_reg.call_args[0][0].statement.compile(db.engine)
                expected = session.query(
                    Alert1.model
                ).filter(*Alert1.conditions).statement.compile(db.engine)
                self.assertEquals(str(actual), str(expected))
                self.assertEquals(actual.params, expected.params)

    @mock.patch("tests.alerts.Alert1.auto_register", False)
    @mock.patch("tests.alerts.Alert1.filter_registered", lambda s, q: q)
    def test_manual_register_register(self):
        sample_id = None
        with db.session_scope() as session:
            sample = SampleModel(name="catch_alert")
            session.add(sample)
            session.commit()
            sample_id = sample.id

        with self.assertRaises(NotImplementedError):
            run.execute_alert(Alert1, sync=True)

        called_with = []

        def reg(self, obj):
            called_with.append({"id": obj.id, "name": obj.name})

        with mock.patch("tests.alerts.Alert1.register", reg):
            run.execute_alert(Alert1, sync=True)
            self.assertEquals(len(called_with), 1)
            with db.session_scope() as session:
                actual = called_with[0]
                sample = session.query(SampleModel).get(sample_id)
                self.assertEquals(actual["id"], sample.id)
                self.assertEquals(actual["name"], sample.name)

    @mock.patch("smtplib.SMTP")
    def test_email_endpoint(self, smtp):
        with db.session_scope() as session:
            sample = SampleModel(name="catch_alert")
            session.add(sample)
            session.commit()

        to = ["foo@faa.com"]
        alert_to = ep.Email(to)
        with mock.patch("tests.alerts.Alert1.alert_to", [alert_to]):
            run.execute_alert(Alert1, sync=True)
            actual = alert_to.server.sendmail.call_args[0][:2]
            expected = (conf.settings.EMAIL["user"], to)
            self.assertEquals(actual, expected)


class EmailEndpoint(BaseTest):

    def test_sent_from(self):
        self.assertEquals(
            ep.Email(["foo@faa.com"]).get_sent_from(None),
            conf.settings.EMAIL["user"])
        self.assertEquals(
            ep.Email(["foo@faa.com"], sent_from="faa").get_sent_from(None),
            "faa")
        newkeys = {"user": "foo", "server": "coso"}
        with mock.patch.dict(conf.settings.EMAIL, newkeys):
            self.assertEquals(
                ep.Email(["foo@faa.com"]).get_sent_from(None), "foo@coso")

    def test_subject(self):
        self.assertEquals(
            ep.Email([""], subject="foo").get_subject(None), "foo")

    def test_message(self):
        self.assertEquals(
            ep.Email([""], message="foo - {}").get_message("faa"), "foo - faa")


class FileEndpoint(BaseTest):

    def test_memory(self):
        f = ep.File(":memory:")
        f.setup(None)
        self.assertIsInstance(f.fp, six.StringIO)

    @mock.patch("codecs.open")
    def test_file(self, codecs_open):
        f = ep.File("foo")
        f.setup(None)
        codecs_open.assert_called_once_with("foo", "a", "utf8")
        f.teardown(None, None, None)

    def test_real_file(self):
        fd, path = tempfile.mkstemp()
        try:
            f = ep.File(path)
            f.setup(None)
            f.teardown(None, None, None)
        finally:
            if fd:
                os.close(fd)
                os.remove(path)
