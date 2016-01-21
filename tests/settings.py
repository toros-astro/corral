#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# IMPORTS
# =============================================================================

import logging
import os

# =============================================================================
# CONF
# =============================================================================

PATH = os.path.abspath(os.path.dirname(__file__))

DEBUG_PROCESS = True

LOG_LEVEL = logging.WARNING

PIPELINE_SETUP = "tests.pipeline.TestPipeline"

CONNECTION = 'sqlite:///:memory:'

LOADER = "tests.steps.TestLoader"

STEPS = ["tests.steps.Step1", "tests.steps.Step2"]

ALERTS = ["tests.alerts.Alert1"]

SHELL_LOCALS = {"foo": 1}

EMAIL = {
    "server": "smtp.foo.com:587",
    "tls": True,
    "user": "foo@foo.com",
    "password": "secret"
}

MIGRATIONS_SETTINGS = os.path.join(PATH, "migrations", "alembic.ini")
