#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# DOC
# =============================================================================

"""All settings tests"""


# =============================================================================
# IMPORTS
# =============================================================================

import mock

from corral import docs, run, res, db, qa

from .models import SampleModel
from .base import BaseTest


# =============================================================================
# BASE CLASS
# =============================================================================

class TestModelsDiagram(BaseTest):

    def test_models_diagram(self):
        with mock.patch("sadisplay.describe") as describe, \
                mock.patch("sadisplay.dot") as dot:
                    docs.models_diagram()
                    describe.assert_called_with(
                        [SampleModel],
                        show_methods=True,
                        show_properties=True,
                        show_indexes=True)
                    dot.assert_called_with(describe())


class TestCreateDoc(BaseTest):

    def test_create_doc(self):
        processors = (
            [run.load_loader()] +
            list(run.load_alerts()) +
            list(run.load_steps()))
        models = db.get_models(False)
        template_path = res.fullpath("doc.md")
        with mock.patch("codecs.open") as copen, \
                mock.patch("jinja2.Template") as template:
                    docs.create_doc(processors, models, doc_formatter=None)
                    copen.assert_called_with(template_path, encoding="utf8")
                    with copen() as fp:
                        template.assert_called_with(fp.read())
                    template().render.assert_called()


class TestQAReport(BaseTest):

    def test_qa_report(self):
        report = mock.MagicMock(spec=qa.QAResult)
        full_output = mock.MagicMock()
        template_path = res.fullpath("qa_report.md")
        with mock.patch("codecs.open") as copen, \
                mock.patch("jinja2.Template") as template:
                    docs.qa_report(report, full_output, explain_qai=True)
                    copen.assert_called_with(template_path, encoding="utf8")
                    with copen() as fp:
                        template.assert_called_with(fp.read())
                    template().render.assert_called()
