#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016-2017, Cabral, Juan; Sanchez, Bruno & Berois, Martín
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# * Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.

# * Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# =============================================================================
# IMPORT
# =============================================================================

import abc
import logging
import datetime
import unittest
import inspect
import pkgutil
import os
import sys
import tempfile
import multiprocessing
import math
from collections import defaultdict

import six

import mock

import xmltodict

from flake8 import engine, reporter

import sh

import attr

from . import util, core, db, run, cli
from .db import database_exists, create_database, drop_database
from .exceptions import ImproperlyConfigured
from .run.base import Processor

conf = util.dimport("corral.conf", lazy=True)


# =============================================================================
# CONSTANTS
# =============================================================================

IS_WINDOWS = sys.platform.startswith("win")

DEFAULT_SCORE_CUALIFICATIONS = {
    0: "F",
    60: "D-",
    63: "D",
    67: "D+",
    70: "C-",
    73: "C",
    77: "C+",
    80: "B-",
    83: "B",
    87: "B+",
    90: "A-",
    93: "A",
    95: "A+"
}

DEFAULT_TAU = 13


# =============================================================================
# TEST CASE
# =============================================================================

@attr.s(frozen=True)
class CommandStatus(object):
    arguments = attr.ib()
    kwargs = attr.ib()
    gkwargs = attr.ib()
    out = attr.ib()
    err = attr.ib()
    exit_status = attr.ib()


class CorralPatch(object):

    def __init__(self):
        self._mocked = []

    def __call__(self, *args, **kwargs):
        mck = mock.patch(*args, **kwargs)
        mck.start()
        self._mocked.append(mck)
        return mck

    def dict(self, *args, **kwargs):
        mck = mock.patch.dict(*args, **kwargs)
        mck.start()
        self._mocked.append(mck)
        return mck

    def object(self, *args, **kwargs):
        mck = mock.patch.object(*args, **kwargs)
        mck.start()
        self._mocked.append(mck)
        return mck

    def multiple(self, *args, **kwargs):
        mck = mock.patch.multiple(*args, **kwargs)
        mck.start()
        self._mocked.append(mck)
        return mck

    def stop(self):
        for mck in reversed(self._mocked):
            mck.stop()


@six.add_metaclass(abc.ABCMeta)
class TestCase(unittest.TestCase):

    # Mostly for internal use
    @classmethod
    def get_subject(cls):
        return getattr(cls, "subject", None)

    def __init__(self, conn, proc_or_cmd):
        super(TestCase, self).__init__()
        self.__conn = conn
        self.__proc_or_cmd = proc_or_cmd
        self.__session = None
        self.__patch = CorralPatch()
        self.__enabled_patch = False
        self.__cliargs = []
        self.__command_status = None

    def runTest(self):
        try:
            with db.session_scope() as session:
                self.__session = session
                self.__enabled_patch = True
                self.setup()
                self.__enabled_patch = False
            self.execute()
            with db.session_scope() as session:
                self.__session = session
                self.validate()
        finally:
            with db.session_scope() as session:
                self.__session = session
                self.teardown()

    def setUp(self):
        if database_exists(self.conn):
            drop_database(self.conn)
        create_database(self.conn)
        db.create_all()

    def execute(self):
        poc = self.__proc_or_cmd
        if issubclass(poc, run.Loader):
            run.execute_loader(poc, sync=True)
        elif issubclass(poc, run.Step):
            run.execute_step(poc, sync=True)
        elif issubclass(poc, run.Alert):
            run.execute_alert(poc, sync=True)
        elif issubclass(poc, cli.BaseCommand):
            parser = cli.create_parser()
            options = poc.get_options()
            arguments = [options["title"]] + self.__cliargs
            out, err = six.StringIO(), six.StringIO()
            command, mode, kwargs, gkwargs = parser.parse_args(arguments)
            with mock.patch("sys.stdout", out), mock.patch("sys.stderr", err):
                command.handle(**kwargs)
            self.__command_status = CommandStatus(
                arguments=arguments, kwargs=kwargs, gkwargs=gkwargs,
                out=out.getvalue(), err=err.getvalue(),
                exit_status=command.exit_status)

    # mostly the public api
    def setup(self):
        pass

    @abc.abstractmethod
    def validate(self):
        raise NotImplementedError()

    def tearDown(self):
        if database_exists(self.conn):
            drop_database(self.conn)
        self.__patch.stop()

    def teardown(self):
        pass

    # ASSERT

    # PY2 COMP
    if six.PY2:
        assertRaisesRegex = six.assertRaisesRegex
        assertCountEqual = six.assertCountEqual

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

    # mostly for setup
    def save(self, obj):
        if isinstance(obj, db.Model):
            self.session.add(obj)

    def delete(self, obj):
        if isinstance(obj, db.Model):
            self.session.delete(obj)

    @property
    def proc_or_cmd(self):
        return self.__proc_or_cmd

    @property
    def session(self):
        return self.__session

    @property
    def conn(self):
        return self.__conn

    @property
    def patch(self):
        if not self.__enabled_patch:
            raise AttributeError("patch can only be accessible from setup()")
        return self.__patch

    @property
    def cliargs(self):
        if not self.__enabled_patch:
            raise AttributeError("cliargs can only be accessible from setup()")
        return self.__cliargs

    @property
    def command_status(self):
        return self.__command_status


class QAResult(object):

    def __init__(self, project_modules, processors, commands,
                 ts_report, ts_out, cov_report, style_report):
        self._project_modules = tuple(project_modules)
        self._processors = tuple(processors)
        self._commands = tuple(commands)
        self._ts_report = ts_report
        self._ts_out = ts_out
        self._cov_report, self._cov_xml = cov_report
        self._style_report, self._style_report_text = style_report
        self._created_at = datetime.datetime.utcnow()

    @property
    def created_at(self):
        return self._created_at

    @property
    def qai(self):
        """QAI = 2 * (TP * (T/PNC) * COV) / (1 + exp(MSE/tau))

        Where:
            TP: If all tests passes is 1, 0 otherwise.
            T: The number of test cases.
            PCN: The number number of processors (Loader, Steps and Alerts)
                 and commands.
            COV: The code coverage (between 0 and 1).
            MSE: The Maintainability and Style Errors.
            tau: Tolerance of style errors per file

        """
        TP = 1. if self.is_test_sucess else 0.
        PCN = self.processors_number + self.commands_number
        T_div_PCN = float(self.test_runs) / PCN
        COV = self.coverage_line_rate
        tau = get_tau()

        total_tau = float(tau) * len(self.project_modules)
        style = 1 + math.exp(self.style_errors / total_tau)

        result = (2 * TP * T_div_PCN * COV) / style
        return result

    @property
    def cualification(self):
        score_cualifications = get_score_cualifications()
        qai_100 = self.qai * 100
        for lowlimit, c in sorted(score_cualifications.items(), reverse=True):
            if qai_100 >= lowlimit:
                return c

    @property
    def project_modules(self):
        return self._project_modules

    @property
    def coverage_report(self):
        return six.text_type(self._cov_report)

    @property
    def style_report(self):
        return six.text_type(self._style_report_text)

    @property
    def test_report(self):
        return self._ts_out

    @property
    def is_test_sucess(self):
        return self._ts_report.wasSuccessful()

    @property
    def test_runs(self):
        return self._ts_report.testsRun

    @property
    def processors_number(self):
        return len(self._processors)

    @property
    def commands_number(self):
        return len(self._commands)

    @property
    def coverage_line_rate(self):
        return float(self._cov_xml["coverage"]["@line-rate"])

    @property
    def style_errors(self):
        return self._style_report.total_errors


# =============================================================================
# FUNCTIONS
# =============================================================================

def get_test_module_name():
    return "{}.tests".format(conf.PACKAGE)


def get_test_module():
    return util.dimport(get_test_module_name())


def get_tau():
    return conf.settings.get("QAI_TAU", DEFAULT_TAU)


def get_score_cualifications():
    return conf.settings.get("SCORE_CUALIFICATIONS",
                             DEFAULT_SCORE_CUALIFICATIONS)


def retrieve_all_pipeline_modules_names():

    def extract_modules(cls_names):
        modules = []
        for cls_name in cls_names:
            cls = util.dimport(cls_name)
            modules.append(cls.__module__)
        return modules

    def recursive_search(pkg_name):
        modules = []
        pkg = util.dimport(pkg_name)
        for mod, mod_name, is_pkg in pkgutil.iter_modules(pkg.__path__):
            mod_fullname = ".".join([pkg_name, mod_name])
            modules.append(mod_fullname)
            if is_pkg:
                modules.extend(recursive_search(mod_fullname))
        return modules

    models_module = db.load_models_module().__name__
    commands_module = cli.load_commands_module().__name__
    modules_names = [
        get_test_module_name(),
        models_module, commands_module,
        conf.CORRAL_SETTINGS_MODULE, conf.PACKAGE]
    modules_names.extend(extract_modules([
        conf.settings.PIPELINE_SETUP,
        conf.settings.LOADER]))
    modules_names.extend(extract_modules(conf.settings.STEPS))
    modules_names.extend(extract_modules(conf.settings.ALERTS))
    modules_names.extend(recursive_search(conf.PACKAGE))

    return tuple(set(modules_names))


def get_testcases(processors, commands, test_module):
    buff = defaultdict(list)
    for cls in vars(test_module).values():
        if inspect.isclass(cls) and issubclass(cls, TestCase):
            subject = cls.get_subject()
            if not issubclass(subject, (Processor, cli.BaseCommand)):
                msg = (
                    "'{}' subject must be a Processor or BaseCommand instance."
                    " Found '{}'")
                raise ImproperlyConfigured(msg.format(subject, type(subject)))
            buff[subject].append(cls)

    db_url = db.get_url(core.in_test())
    testscases = []
    for proc in processors:
        tests = [cls(db_url, proc) for cls in buff[proc]]
        testscases.append((proc, tests))
    for cmd in commands:
        tests = [cls(db_url, cmd) for cls in buff[cmd]]
        testscases.append((cmd, tests))
    return testscases


def run_tests(processors, commands, failfast, verbosity,
              default_logging=False, stream=sys.stderr):
    if not default_logging:
        for k, logger in logging.Logger.manager.loggerDict.items():
            if k.startswith("Corral") or k.startswith("sqlalchemy"):
                if isinstance(logger, logging.Logger):
                    logger.setLevel(logging.WARNING)

    suite = unittest.TestSuite()
    test_module = get_test_module()
    testcases = get_testcases(processors, commands, test_module)
    for _, tests in testcases:
        suite.addTests(tests)

    runner = unittest.runner.TextTestRunner(
        stream=stream, verbosity=verbosity, failfast=failfast)
    suite_result = runner.run(suite)
    return suite_result


def run_coverage(failfast, verbosity, default_logging=False):
    report, xml_report = None, None

    executable = os.path.join(os.getcwd(), sys.argv[0])
    to_coverage = ",".join(retrieve_all_pipeline_modules_names())

    params = {"_ok_code": [0, 1]}
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
    exclude_paths = [
        os.path.join(path, "migrations", "versions") for path in paths]

    for path in exclude_paths:
        pep8.options.exclude.append(path)
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


def qa_report(processors, commands, *args, **kwargs):
    core.logger.info("Running Test, Coverage and Style Check. Please Wait...")
    ts_stream = six.StringIO()
    ts_result = run_tests(
        processors, commands, failfast=False, stream=ts_stream, verbosity=2,
        *args, **kwargs)

    cov_result = run_coverage(
        failfast=False, verbosity=0, default_logging=False)

    style_result = run_style()
    project_modules = retrieve_all_pipeline_modules_names()

    report = QAResult(
        project_modules, processors, commands,
        ts_result, ts_stream.getvalue(), cov_result, style_result)

    return report
