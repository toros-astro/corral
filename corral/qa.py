#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# IMPORT
# =============================================================================

import abc
import logging
import unittest
import inspect
import pkgutil
import os
import sys
import tempfile
import multiprocessing
import datetime
import codecs
from collections import defaultdict, OrderedDict

import six

import mock

import xmltodict

from flake8 import engine, reporter

import sh

import jinja2

from . import util, conf, core, db, run, cli, setup, res
from .db import database_exists, create_database, drop_database
from .exceptions import ImproperlyConfigured
from .run.base import Processor


# =============================================================================
# CONSTANTS
# =============================================================================

TESTS_MODULE = "{}.tests".format(conf.PACKAGE)

IS_WINDOWS = sys.platform.startswith("win")

DEFAULT_SCORE_COMMENTS = {
    0: "F",
    1: "F+",
    2: "E",
    3: "E+",
    4: "D",
    5: "D+",
    6: "C",
    7: "C+",
    8: "B",
    9: "A",
    10: "A+"
}

SCORE_COMMENTS = conf.settings.get("SCORE_COMMENTS", DEFAULT_SCORE_COMMENTS)


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


class QAResult(object):

    def __init__(self, processors, ts_report, cov_report, style_report):
        self._processors = processors
        self._ts_report = ts_report
        self._cov_report, self._cov_xml = cov_report
        self._style_report, self._style_report_text = style_report

    def qai(self):
        """QAI = (TP * (T/PN) * COV) / (1+MSE)

        Where:
            TP: If all tests passes is 1, 0 otherwise.
            T: The number of test cases.
            PN: The number number of processors (Loader, Steps and Alerts).
            COV: The code coverage (between 0 and 1).
            MSE: The Maintainability and Style Errors.

        """
        works = 1. if self._ts_report.wasSuccessful() else 0.
        test_by_procs = float(self._ts_report.testsRun) / len(self._processors)
        cov = float(self._cov_xml["coverage"]["@line-rate"])
        style = 1. + self._style_report.total_errors
        return (works * test_by_procs * cov) / style

    def qai_score(self):
        qai_10 = int(round(self.qai() * 10))
        return SCORE_COMMENTS.get(qai_10, str(qai_10))

    def full_output(self):
        return "\n".join(
            ["", "**** COVERAGE ****", str(self._cov_report), "-" * 80] +
            ["", "**** MAINTAINABILITY & STYLE ****",
             self._style_report_text, "-" * 80])

    def resume(self):
        data = OrderedDict()
        data["Tests Sucess"] = self._ts_report.wasSuccessful()
        data["Test Number"] = self._ts_report.testsRun
        data["Procesors Number"] = len(self._processors)
        data["Coverage (%)"] = "{:.2f}%".format(
            float(self._cov_xml["coverage"]["@line-rate"]) * 100)
        data["Maintainability & Style Errors"] = (
            self._style_report.total_errors)
        data["-> QA Index (%)"] = "{0:.2f}%".format(self.qai() * 100)
        data["-> QA Score"] = self.qai_score()
        return data


# =============================================================================
# FUNCTIONS
# =============================================================================

def get_test_module():
    return util.dimport(TESTS_MODULE)


def retrieve_all_pipeline_modules_names():

    def recursive_search(pkg_name):
        modules = []
        pkg = util.dimport(pkg_name)
        for mod, mod_name, is_pkg in pkgutil.iter_modules(pkg.__path__):
            mod_fullname = ".".join([pkg_name, mod_name])
            modules.append(mod_fullname)
            if is_pkg:
                modules.extend(recursive_search(mod_fullname))
        return modules

    modules_names = [
        TESTS_MODULE,
        db.MODELS_MODULE, cli.COMMANDS_MODULE,
        conf.CORRAL_SETTINGS_MODULE, conf.PACKAGE,
        conf.settings.PIPELINE_SETUP, conf.settings.PIPELINE_SETUP,
        conf.settings.LOADER]
    modules_names.extend(conf.settings.STEPS)
    modules_names.extend(conf.settings.ALERTS)
    modules_names.extend(recursive_search(conf.PACKAGE))
    return tuple(set(modules_names))


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

    suite = unittest.TestSuite()
    test_module = get_test_module()
    testcases = get_processors_testcases(processors, test_module)
    for _, tests in testcases:
        suite.addTests(tests)

    runner = unittest.runner.TextTestRunner(
        verbosity=verbosity, failfast=failfast)
    suite_result = runner.run(suite)
    return suite_result


def run_coverage(failfast, verbosity, default_logging=False):
    report, xml_report = None, None

    executable = os.path.join(os.getcwd(), sys.argv[0])
    to_coverage = ",".join(retrieve_all_pipeline_modules_names())

    params = {}
    if failfast:
        params["failfast"] = True
    if verbosity == 1:
        params["verbose"] = True
    elif verbosity > 1:
        params["vverbose"] = True
    if default_logging:
        params["default-logging"] = True

    sh.coverage.erase()
    try:
        sh.coverage.run("--source", to_coverage, executable, "test", **params)
    except sh.ErrorReturnCode as err:
        core.logger.error(err)

    report = sh.coverage.report()

    with tempfile.NamedTemporaryFile() as tfp:
        sh.coverage.xml(ignore_errors=True, o=tfp.name, _no_out=True)
        with open(tfp.name) as fp:
            xml_src = fp.read()
            xml_report = xmltodict.parse(xml_src)

    return report, xml_report


def run_style():

    prj_path = util.dimport(conf.PACKAGE).__file__
    prj_path_len = len(os.path.dirname(os.path.dirname(prj_path)))

    # THANKS
    # https://github.com/oTree-org/otree-core/blob/96d6ffa/tests/test_style.py
    class FileCollectReport(reporter.QueueReport):

        def __init__(self, *args, **kwargs):
            super(FileCollectReport, self).__init__(*args, **kwargs)
            self._errs_queue = multiprocessing.Queue()
            self._errors = []

        def error(self, line_number, offset, text, check):
            super(FileCollectReport, self).error(
                line_number, offset, text, check)
            self._errs_queue.put((self.filename, line_number, offset, text))

        def error_list(self):
            while self._errs_queue.qsize():
                filepath, line_number, offset, text = (
                    self._errs_queue.get_nowait())
                filename = filepath[prj_path_len:]
                error = u"{}:{}:{}: {}".format(
                    filename, line_number, offset, text)
                self._errors.append(error)
            return tuple(self._errors)

    def configure_pep8():
        if IS_WINDOWS:
            # WINDOWS UGLY AND HACKISH PATCH for flake 8 is based on
            # http://goo.gl/2b53SG
            sys.argv.append(".")
            pep8 = engine.get_style_guide(jobs=1)
        else:
            pep8 = engine.get_style_guide()

        pep8.reporter = FileCollectReport
        report = pep8.init_report(pep8.reporter)
        report.input_file = pep8.input_file
        pep8.runner = report.task_queue.put
        return pep8

    pep8 = configure_pep8()
    mod_names = retrieve_all_pipeline_modules_names()
    top_mod_names = set([mn.split(".", 1)[0] for mn in mod_names])
    paths = [
        os.path.dirname(util.dimport(mn).__file__) for mn in top_mod_names]

    for path in paths:
        pep8.paths.append(path)

    with mock.patch("sys.stdout"):
        report = pep8.check_files()

    if report.total_errors:
            lines = ["Found pep8-style errors."]
            lines.append(
                "Please check the Python code style reference: "
                "https://www.python.org/dev/peps/pep-0008/"
            )
            lines.append("\nErrors found: ")
            for error in report.error_list():
                if error.startswith("/") or error.startswith("\\"):
                    error = error[1:]
                lines.append(error)
            text = "\n".join(lines)
    else:
        text = ""
    return report, text


def qa_report(processors, verbosity, *args, **kwargs):
    ts_result = run_tests(
        processors, failfast=False, verbosity=verbosity, *args, **kwargs)
    cov_result = run_coverage(
        failfast=False, verbosity=0, default_logging=False)
    style_result = run_style()
    report = QAResult(processors, ts_result, cov_result, style_result)
    return report


def create_doc(processors, models, doc_formatter=None):

    if doc_formatter is None:
        def doc_formatter(string):
            lines = [s.strip() for s in string.splitlines()]
            return "\n".join(lines)

    path = res.fullpath("doc_template.md")
    with codecs.open(path, encoding="utf8") as fp:
        template = jinja2.Template(fp.read())

    loader, steps, alerts = None, [], []
    for proc in processors:
        if issubclass(proc, run.Loader):
            loader = proc
        elif issubclass(proc, run.Step):
            steps.append(proc)
        elif issubclass(proc, run.Alert):
            alerts.append(proc)

    cli_help = cli.create_parser().main_help_text(0)

    ctx = {
        "doc_formatter": doc_formatter,
        "now": datetime.datetime.now(), "core": core,
        "pipeline_setup": setup.load_pipeline_setup(), "cli_help": cli_help,
        "models": models, "loader": loader, "steps": steps, "alerts": alerts}

    return template.render(**ctx)
