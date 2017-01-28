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
# IMPORTS
# =============================================================================

import sys
import datetime
import codecs

import jinja2

import sadisplay

from . import cli, core, res, setup, run, util, db, qa


# =============================================================================
# FUNCTIONS
# =============================================================================

def models_diagram():
    default_models = db.load_default_models()
    models = [
        m for m in util.collect_subclasses(db.Model)
        if sys.modules[m.__module__] != default_models]

    desc = sadisplay.describe(
        models,
        show_methods=True,
        show_properties=True,
        show_indexes=True)

    return sadisplay.dot(desc)


def create_doc(processors, models, doc_formatter=None):

    def get_cli_text():
        def scmd_fmt(scmd, htext):
            return "- ``{}``: {}".format(scmd, htext)

        parser = cli.create_parser()

        usage = [
            "", parser.global_parser.usage, "", "Available subcommands", ""]
        usage.extend(["**CORRAL**", ""])
        usage.extend(
                scmd_fmt(hparts[0], hparts[1])
                for hparts in sorted(parser.help_texts["corral"]))

        pkgs = [k for k in parser.help_texts.keys() if k != "corral"]
        for pkg in pkgs:
            usage.extend(["", "**" + pkg.upper() + "**", ""])
            usage.extend(
                scmd_fmt(hparts[0], hparts[1])
                for hparts in sorted(parser.help_texts[pkg]))

        return "\n".join(usage)

    if doc_formatter is None:
        def doc_formatter(string):
            lines = [s.strip() for s in string.splitlines()]
            return "\n".join(lines)

    path = res.fullpath("doc.md")
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

    cli_help = get_cli_text()

    ctx = {
        "doc_formatter": doc_formatter,
        "now": datetime.datetime.now(), "core": core,
        "pipeline_setup": setup.load_pipeline_setup(), "cli_help": cli_help,
        "models": models, "loader": loader, "steps": steps, "alerts": alerts}

    return template.render(**ctx)


def qa_report(report, full_output, explain_qai):
    path = res.fullpath("qa_report.md")
    score_cualifications = qa.get_score_cualifications()

    with codecs.open(path, encoding="utf8") as fp:
        template = jinja2.Template(fp.read())
    ctx = {
        "report": report, "full_output": full_output,
        "explain_qai": explain_qai, "qai_doc": report.__class__.qai.__doc__,
        "tau": qa.get_tau(), "core": core,
        "cualifications": sorted(score_cualifications.items()),
        "pipeline_setup": setup.load_pipeline_setup()}

    return template.render(**ctx)
