#!/usr/bin/env python
# -*- coding: utf-8 -*-

import keyword
import string
import codecs
import datetime
import os
import re
import shutil

import six

from .core import logger, get_version
from .exceptions import ValidationError


# =============================================================================
# CONSTANTS
# =============================================================================

KEYWORDS = frozenset(keyword.kwlist)

BUILTINS = frozenset(dir(six.moves.builtins))

FORBIDEN_WORDS = frozenset((
    "True", "False", "None", "corral", "__builtins__", "builtins",
    "models", "tests", "command", "migrations", "in_corral.py", "in_corral",
    "settings", "load", "steps", "__init__", "test", "alembic", "migrations"))

IDENTIFIER = re.compile(r"^[^\d\W]\w*\Z", re.UNICODE)

PATH = os.path.abspath(os.path.dirname(__file__))

PIPELINE_TEMPLATE_PATH = os.path.join(PATH, "template")

UNSUGESTED_NAMES = set()

TEMPLATES = []

for dpath, dnames, fnames in os.walk(PIPELINE_TEMPLATE_PATH):
    for fname in fnames:
        TEMPLATES.append(os.path.join(dpath, fname))
    UNSUGESTED_NAMES.update(os.path.splitext(fn)[0] for fn in fnames)
    UNSUGESTED_NAMES.update(os.path.splitext(dn)[0] for dn in dnames)

EXCLUDE_APPLY_CONTEXT = ("script.py.mako",)


# =============================================================================
# FUNCTIONS
# =============================================================================

def validate_name(name):
    msg = "'{}' {}"
    if name in KEYWORDS:
        raise ValidationError(msg.format(name, "is a keyword"))
    elif name in BUILTINS:
        raise ValidationError(msg.format(name, "is a builtin"))
    elif name in FORBIDEN_WORDS:
        raise ValidationError(msg.format(name, "is a forbiden word"))
    elif not re.match(IDENTIFIER, name):
        raise ValidationError("Invalid identifier '{}'".format(name))
    elif name in UNSUGESTED_NAMES:
        raise ValidationError(
            msg.format(name, "has a conflict with default pipeline names"))


def create_pipeline(path):
    fpath = os.path.abspath(path)
    basename = os.path.basename(path)

    validate_name(basename)

    if os.path.isdir(fpath):
        raise ValidationError("directory '{}' already exists".format(fpath))

    logger.info("Creating pipelin in '{}'...".format(fpath))

    context = {
        "project_name": basename,
        "timestamp": datetime.datetime.now().isoformat(),
        "version": get_version(),
        "migration_script": os.path.join(basename, "migrations")}

    for tpl_path in TEMPLATES:

        rel_path = tpl_path.replace(
                PIPELINE_TEMPLATE_PATH, "", 1)
        while rel_path.startswith(os.path.sep):
            rel_path = rel_path[1:]
        dest_path = os.path.join(fpath, rel_path)

        dest_dir = os.path.dirname(dest_path)
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)

        tpl_name = os.path.basename(tpl_path)
        if tpl_name in EXCLUDE_APPLY_CONTEXT:
            shutil.copy(tpl_path, dest_path)
            continue

        with codecs.open(tpl_path, encoding="utf-8") as fp:
                tpl = string.Template(fp.read())

        src = tpl.safe_substitute(context)

        with codecs.open(dest_path, "w", encoding="utf-8") as fp:
            fp.write(src)

    rename_from = os.path.join(fpath, "template")
    rename_to = os.path.join(fpath, basename)
    shutil.move(rename_from, rename_to)

    logger.info("Success!")
