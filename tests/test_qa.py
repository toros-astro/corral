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

from corral import qa

import mock

from . import tests
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
