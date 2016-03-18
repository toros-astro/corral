#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# IMPORT
# =============================================================================

import abc
import logging
import unittest
import inspect
from collections import defaultdict

import six

from . import util, conf, core, db, run
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

    def __init__(self, conn, proc):
        super(TestCase, self).__init__()
        self.__conn = conn
        self.__proc = proc
        self.__session = None

    def runTest(self):
        with db.session_scope() as session:
            self.__session = session
            self.setup()
        self.execute_processor()
        with db.session_scope() as session:
            self.__session = session
            self.validate()

        with db.session_scope() as session:
            self.__session = session
            self.teardown()

    def setUp(self):
        if database_exists(self.conn):
            drop_database(self.conn)
        create_database(self.conn)
        db.create_all()

    def setup(self):
        pass

    def execute_processor(self):
        proc = self.__proc
        if issubclass(proc, run.Loader):
            run.execute_loader(self.proc, sync=True)
        elif issubclass(proc, run.Step):
            run.execute_step(proc, sync=True)
        elif issubclass(proc, run.Alert):
            run.execute_alert(proc, sync=True)

    @abc.abstractmethod
    def validate(self):
        raise NotImplementedError()

    def tearDown(self):
        if database_exists(self.conn):
            drop_database(self.conn)

    def teardown(self):
        pass

    # PY2 COMP
    if six.PY2:
        assertRaisesRegex = six.assertRaisesRegex
        assertCountEqual = six.assertCountEqual

    # asserts
    def save(self, obj):
        if isinstance(obj, db.Model):
            self.session.add(obj)

    def delete(self, obj):
        if isinstance(obj, db.Model):
            self.session.delete(obj)

    def assertStreamHas(self, model, *filters):
        query = self.__session.query(model)
        if filters:
            query = query.filter(*filters)
        if query.count() == 0:
            filters_str = ", ".join(["'{}'".format(str(f)) for f in filters])
            msg = "Model '{}' with filters {} not found".format(
                model.__name__, filters_str)
            self.fail(msg)

    def assertStreamHasNot(self, model, *filters):
        query = self.__session.query(model)
        if filters:
            query = query.filter(*filters)
        if query.count() != 0:
            filters_str = ", ".join(["'{}'".format(str(f)) for f in filters])
            msg = "Model '{}' with filters {} found".format(
                model.__name__, filters_str)
            self.fail(msg)

    def assertStreamCount(self, expected, model, *filters):
        query = self.__session.query(model)
        if filters:
            query = query.filter(*filters)
        self.assertEquals(query.count(), expected)

    @property
    def processor(self):
        return self.__proc

    @property
    def session(self):
        return self.__session

    @property
    def conn(self):
        return self.__conn


class Result(object):

    def __init__(self, proc, ts_result):
        self.proc = proc
        self.ts_result = ts_result


# =============================================================================
# FUNCTIONS
# =============================================================================

def get_test_module():
    return util.dimport(TESTS_MODULE)


def is_partial_test(processors):
    # loader + steps + alerts
    total_number_proc_procs = (
        1 + len(conf.settings.STEPS) + len(conf.settings.ALERTS))
    return len(processors) < total_number_proc_procs


def get_processors_testcases(processors, test_module):
    buff = defaultdict(list)
    for cls in vars(test_module).values():
        if inspect.isclass(cls) and issubclass(cls, TestCase):
            subject = cls.get_subject()
            if not issubclass(subject, Processor):
                msg = "'{}' subject must be a Processor instance. Found '{}'"
                raise ImproperlyConfigured(msg.format(subject, type(subject)))
            buff[subject].append(cls)

    db_url = db.get_url(core.in_test())
    testscases = []
    for proc in processors:
        tests = [cls(db_url, proc) for cls in buff[proc]]
        testscases.append((proc, tests))
    return testscases


def run_tests(processors, failfast, verbosity, default_logging=False):
    if not default_logging:
        for k, logger in logging.Logger.manager.loggerDict.items():
            if k.startswith("Corral") or k.startswith("sqlalchemy"):
                if isinstance(logger, logging.Logger):
                    logger.setLevel(logging.WARNING)

    test_module = get_test_module()
    testcases = get_processors_testcases(processors, test_module)
    is_partial = is_partial_test(processors)
    results = []

    for proc, tests in testcases:
        suite = unittest.TestSuite()
        suite.addTests(tests)
        runner = unittest.runner.TextTestRunner(
            verbosity=verbosity, failfast=failfast)
        suite_result = runner.run(suite)
        result =  Result(proc, suite_result)
        results.append(result)
