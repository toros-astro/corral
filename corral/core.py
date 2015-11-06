#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import keyword
import string
import codecs
import datetime
import os

import six

from . import VERSION, DOC
from .exceptions import ValidationError


# =============================================================================
# CONSTANTS
# =============================================================================

KEYWORDS = frozenset(keyword.kwlist)

BUILTINS = frozenset(dir(six.moves.builtins))

FORBIDEN_WORDS = frozenset(("True", "False", "None", "corral"))

PATH = os.path.abspath(os.path.dirname(__file__))

PIPELINE_TEMPLATE_PATH = os.path.join(PATH, "template")

TEMPLATES = [
    (fn, os.path.join(PIPELINE_TEMPLATE_PATH, fn))
    for fn in os.listdir(PIPELINE_TEMPLATE_PATH) if fn != "in_corral.py"]

IN_CORRAL_TEMPLATE = os.path.join(PIPELINE_TEMPLATE_PATH, "in_corral.py")


# =============================================================================
# LOGGER
# =============================================================================

logging.basicConfig(format="[%(asctime)-15s] %(message)s")
logger = logging.getLogger("Corral")


# =============================================================================
# FUNC
# =============================================================================


def get_version():
    return VERSION


def get_description():
    return DOC


def setup_environment():
    from . import db
    db.setup()
    db.load_models_module()


def validate_name(name):
    msg = "'{}' is a {}"
    if name in KEYWORDS:
        raise ValidationError(msg.format(name, "keyword"))
    elif name in BUILTINS:
        raise ValidationError(msg.format(name, "builtin"))
    elif name in FORBIDEN_WORDS:
        raise ValidationError(msg.format(name, "forbiden word"))


def render_pipeline_template(path):
    fpath = os.path.abspath(path)
    basename = os.path.basename(path)

    validate_name(basename)

    if os.path.isdir(fpath):
        raise ValidationError("directory '{}' already exists".format(fpath))

    logger.info("Creating pipelin in '{}'...".format(fpath))
    os.makedirs(fpath)

    context = {
        "project_name": basename,
        "timestamp": datetime.datetime.now().isoformat(),
        "version": get_version}

    for tpl_name, tpl_path in TEMPLATES:
        logger.info("Creating file '{}'...".format(tpl_name))
        with codecs.open(tpl_path, encoding="utf-8") as fp:
            tpl = string.Template(fp.read())

        src = tpl.safe_substitute(context)
        path = os.path.join(fpath, tpl_name)
        with codecs.open(path, "w", encoding="utf-8") as fp:
            fp.write(src)

    logger.info("Creating manager...")
    with codecs.open(IN_CORRAL_TEMPLATE, encoding="utf-8") as fp:
        tpl = string.Template(fp.read())

    src = tpl.safe_substitute(context)
    path = os.path.join(fpath, "..", "in_corral.py")
    with codecs.open(path, "w", encoding="utf-8") as fp:
        fp.write(src)

    logger.info("Success!")
