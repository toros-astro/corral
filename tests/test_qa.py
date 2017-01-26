#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# DOC
# =============================================================================

"""All corral.qa tests"""


# =============================================================================
# IMPORTS
# =============================================================================

import random
import string

import six

import mock

from corral import qa
from corral.exceptions import ImproperlyConfigured

from . import tests, steps, commands
from .base import BaseTest


# =============================================================================
# BASE CLASS
# =============================================================================

class TestGetTestModuleName(BaseTest):

    def test_get_test_module_name(self):
        expected = "tests.tests"
        result = qa.get_test_module_name()
        self.assertEquals(expected, result)


class TestGetModule(BaseTest):

    def test_get_test_module(self):
        expected = tests
        result = qa.get_test_module()
        self.assertIs(expected, result)


class TestGetTau(BaseTest):

    def test_get_tau(self):
        expected = qa.DEFAULT_TAU
        result = qa.get_tau()
        self.assertEquals(result, expected)

        expected = random.randint(1, 100)
        with mock.patch("tests.settings.QAI_TAU", expected, create=True):
            result = qa.get_tau()
            self.assertEquals(result, expected)


class TestGetScoreCualifications(BaseTest):

    def test_get_score_cualifications(self):
        expected = qa.DEFAULT_SCORE_CUALIFICATIONS
        result = qa.get_score_cualifications()
        self.assertEquals(result, expected)

        expected = {
            limit: "".join([random.choice(string.ascii_letters)
                            for _ in range(random.randint(1,  10))])
            for limit in range(0, 100, random.randint(1,  10))
        }
        with mock.patch("tests.settings.SCORE_CUALIFICATIONS",
                        expected, create=True):
            result = qa.get_score_cualifications()
            self.assertEquals(result, expected)


class TestRetrieveAllPipelineModulesNames(BaseTest):

    def test_retrieve_all_pipeline_modules_names(self):
        expected = "tests."
        for result in qa.retrieve_all_pipeline_modules_names():
            msg = "'{}' don't start with '{}'".format(result, expected)
            self.assertTrue(
                result.startswith(expected) or result == expected[:-1], msg)


class TestGetTestcases(BaseTest):

    def test_get_testcases(self):
        for subject, tc in qa.get_testcases([steps.Step1],
                                            [commands.TestAPICommand], tests):
            self.assertTrue(tc)
            for t in tc:
                self.assertIs(t.subject, subject)

    @mock.patch("tests.tests.ExampleTestStep1.subject")
    def test_subject_invalid(self, *args):
        with self.assertRaises(ImproperlyConfigured):
            qa.get_testcases([steps.Step1], [], tests)


class TestRunTest(BaseTest):

    @mock.patch("corral.db")
    @mock.patch("corral.qa.database_exists")
    @mock.patch("corral.qa.create_database")
    @mock.patch("corral.qa.drop_database")
    @mock.patch("unittest.runner._WritelnDecorator")
    def test_run_test(self, *args):
        test_cases = qa.get_testcases([steps.Step1], [], tests)
        expected = len(test_cases[0][1])
        result = qa.run_tests([steps.Step1], [],
                              failfast=False, verbosity=0)
        self.assertEquals(result.testsRun, expected)


class TestRunCoverage(BaseTest):

    @mock.patch("tempfile.NamedTemporaryFile")
    @mock.patch("corral.qa.get_testcases")
    @mock.patch("corral.qa.run_tests")
    @mock.patch("xmltodict.parse", lambda xml: xml)
    @mock.patch('six.moves.builtins.open')
    @mock.patch("sh.coverage")
    def test_run_coverage(self, cov, bopen, xmltodict_parse, *args):
        result = qa.run_coverage(failfast=False, verbosity=0)
        self.assertIs(cov.report(), result[0])
        cov.xml.assert_called()
        with bopen() as fp:
            self.assertIs(fp.read(), result[1])


class TestRunStyle(BaseTest):

    def test_run_style(self):
        modules = qa.retrieve_all_pipeline_modules_names()
        report, text = qa.run_style()
        self.assertEquals(
            report.counters["files"], len(modules) + 1)  # __init__


class TestQAReport(BaseTest):

    @mock.patch("corral.qa.run_tests")
    @mock.patch("corral.qa.run_coverage")
    @mock.patch("corral.qa.run_style")
    def test_qa_report(self, run_style, run_coverage, run_test):
        run_coverage.return_value = (mock.MagicMock(), mock.MagicMock())
        run_style.return_value = (mock.MagicMock(), mock.MagicMock())
        report = qa.qa_report([steps.Step1], [])

        self.assertEquals(
            report.project_modules, qa.retrieve_all_pipeline_modules_names())
        self.assertEquals(report.processors_number, 1)
        self.assertEquals(report.commands_number, 0)
        self.assertEquals(
            report.coverage_report,
            six.text_type(run_coverage.return_value[0]))
        self.assertEquals(
            report.style_report,
            six.text_type(run_style.return_value[1]))
