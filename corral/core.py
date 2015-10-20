#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import db

VERSION = __version__ = ("0", "0", "1")


def get_version():
    return ".".join(VERSION)


def setup_environment():
    db.load_models_module()
