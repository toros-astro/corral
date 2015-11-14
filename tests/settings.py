#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# IMPORTS
# =============================================================================

import logging


# =============================================================================
# CONF
# =============================================================================

LOG_LEVEL = logging.WARNING

PIPELINE_SETUP = "tests.pipeline.TestPipeline"

CONNECTION = 'sqlite:///:memory:'

LOADER = "tests.steps.TestLoader"

STEPS = ["tests.steps.Step1", "tests.steps.Step2"]

SHELL_LOCALS = {"foo": 1}
