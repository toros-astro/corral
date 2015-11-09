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


def setup_environment():
    from . import db, pipeline
    db.setup()
    db.load_models_module()

    setup_cls = pipeline.load_pipeline_setup()
    pipeline.setup_pipeline(setup_cls)
