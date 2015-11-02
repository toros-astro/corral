#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from . import VERSION
from . import db


logging.basicConfig(format="[%(asctime)-15s] %(message)s")
logger = logging.getLogger("Corral")


def get_version():
    return ".".join(VERSION)


def setup_environment():
    db.setup()
    db.load_models_module()
