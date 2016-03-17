#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from . import VERSION, DOC


# =============================================================================
# LOGGER
# =============================================================================

logger = logging.getLogger("Corral")


# =============================================================================
# FUNC
# =============================================================================


def get_version():
    return VERSION


def get_description():
    return DOC


def setup_environment(test_mode=False):
    from . import db, setup
    db.setup(test_connection=test_mode)
    db.load_default_models()
    db.load_models_module()

    setup_cls = setup.load_pipeline_setup()
    setup.setup_pipeline(setup_cls)
