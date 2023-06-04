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
# DOCS
# =============================================================================

"""Allreporting funcionalities tests"""


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
