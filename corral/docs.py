#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# IMPORT
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

def models_diagram(fmt="dot"):
    parsers = {
        "dot": sadisplay.dot,
        "plantuml": sadisplay.plantuml,
    }
    parser = parsers[fmt]

    default_models = db.load_default_models()
    models = [
        m for m in util.collect_subclasses(db.Model)
        if sys.modules[m.__module__] != default_models]

    desc = sadisplay.describe(
        models,
        show_methods=True,
        show_properties=True,
        show_indexes=True)

    return parser(desc)


#~ def pipeline_diagram():
    #~ Node = namedtuple("Node", ["proc", "type", "input", "output"])
    #~ nodes = []

    #~ default_models = db.load_default_models()
    #~ models = [
        #~ m for m in util.collect_subclasses(db.Model)
        #~ if sys.modules[m.__module__] != default_models]

    #~ # check loader
    #~ loader_cls = run.load_loader()
    #~ import ipdb; ipdb.set_trace()

    #~ return parser(desc)


def create_doc(processors, models, doc_formatter=None):

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

    cli_help = cli.create_parser().main_help_text(0)

    ctx = {
        "doc_formatter": doc_formatter,
        "now": datetime.datetime.now(), "core": core,
        "pipeline_setup": setup.load_pipeline_setup(), "cli_help": cli_help,
        "models": models, "loader": loader, "steps": steps, "alerts": alerts}

    return template.render(**ctx)


def qa_report(report, full_output, explain_qai):
    path = res.fullpath("qa_report.md")
    with codecs.open(path, encoding="utf8") as fp:
        template = jinja2.Template(fp.read())

    ctx = {
        "report": report, "full_output": full_output,
        "explain_qai": explain_qai, "qai_doc": type(report).qai.__doc__,
        "tau": qa.TAU, "core": core,
        "cualifications": sorted(qa.SCORE_CUALIFICATIONS.items()),
        "pipeline_setup": setup.load_pipeline_setup()}

    return template.render(**ctx)
