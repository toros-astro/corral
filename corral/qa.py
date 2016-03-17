#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# IMPORT
# =============================================================================

import abc
import unittest
import inspect
from collections import defaultdict

import six

from . import util, conf, core
from .db import database_exists, create_database, drop_database
from .exceptions import ImproperlyConfigured
from .run.base import Processor


# =============================================================================
# CONSTANTS
# =============================================================================

TESTS_MODULE = "{}.tests".format(conf.PACKAGE)


# =============================================================================
# TEST CASE
# =============================================================================

@six.add_metaclass(abc.ABCMeta)
class TestCase(unittest.TestCase):

    @classmethod
    def get_subject(cls):
        return getattr(cls, "subject", None)

    def setUp(self):
        self.setup()
        if database_exists(self.conn):
            drop_database(self.conn)
        create_database(self.conn)

    def setup(self):
        pass

    def tearDown(self):
        self.tearDown()
        if database_exists(self.conn):
            drop_database(self.conn)

    def teardown(self):
        pass

    # PY2 COMP
    if six.PY2:
        assertRaisesRegex = six.assertRaisesRegex
        assertCountEqual = six.assertCountEqual

    # stream asserts
    def assertStreamHas(self, *example_objects):
        pass

    def assertStreamHasNot(self, *example_objects):
        return not self.assertStreamHas(*example_objects)

    def assertStreamCount(self, example_object, expected):
        pass


# =============================================================================
# FUNCTIONS
# =============================================================================

def get_test_module():
    return util.dimport(TESTS_MODULE)


def get_processors_testcases(processors, test_module):
    buff = defaultdict(list)
    for cls in vars(test_module).values():
        if inspect.isclass(cls) and issubclass(cls, TestCase):
            subject = cls.get_subject()
            if not issubclass(subject, Processor):
                msg = "'{}' subject must be a Processor instance. Found '{}'"
                raise ImproperlyConfigured(msg.format(subject, type(subject)))
            buff[subject].append(cls)

    testscases = [(proc, buff[proc]) for proc in processors]
    return testscases


def run_tests(processors, failfast, verbosity):
    test_module = get_test_module()
    testcases = get_processors_testcases(processors, test_module)
    import ipdb; ipdb.set_trace()

