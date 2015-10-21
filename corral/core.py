#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from . import db


VERSION = __version__ = ("0", "0", "1")

logging.basicConfig(format="[%(asctime)-15s] %(message)s'")
logger = logging.getLogger("Corral")


def get_version():
    return ".".join(VERSION)


def setup_environment():
    db.load_models_module()

