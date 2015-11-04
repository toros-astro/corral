#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from . import VERSION, DOC
from . import db


logging.basicConfig(format="[%(asctime)-15s] %(message)s")
logger = logging.getLogger("Corral")


def get_version():
    return VERSION

def get_description():
    return DOC


def setup_environment():
    db.setup()
    db.load_models_module()
