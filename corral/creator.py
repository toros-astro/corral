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

EXCLUDE_EXTS = (".pyc", ".pyo")

UNSUGESTED_NAMES = set()

TEMPLATES = []

for dpath, dnames, fnames in os.walk(PIPELINE_TEMPLATE_PATH):
    for fname in fnames:
        if os.path.splitext(fname)[-1] not in EXCLUDE_EXTS:
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

    logger.info("Creating pipeline in '{}'...".format(fpath))

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

        logger.info(
            "Created '{}'.".format(
                os.path.relpath(dest_path.replace("template", basename))))

    rename_from = os.path.join(fpath, "template")
    rename_to = os.path.join(fpath, basename)
    shutil.move(rename_from, rename_to)

    logger.info("Pipeline {} Ready!!!".format(basename))
