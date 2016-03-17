#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# IMPORT
# =============================================================================

import abc
import unittest

import six

from .db import database_exists, create_database, drop_database
from . import util, conf, core


# =============================================================================
# TEST CASE
# =============================================================================

@six.add_metaclass(abc.ABCMeta)
class TestCase(unittest.TestCase):

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
    import ipdb; ipdb.set_trace()


def run_tests(processors, failfast, verbosity)
    test_module = get_test_module()

