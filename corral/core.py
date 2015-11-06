#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from . import VERSION, DOC


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
