#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created at 2015-12-09T16:33:40.827063 by corral 0.0.1


# =============================================================================
# DOCS
# =============================================================================

"""Global configuration for pipeline

"""


# =============================================================================
# IMPORTS
# =============================================================================

import logging


# =============================================================================
# CONFIGURATIONS
# =============================================================================

#: Sets the threshold for this logger to lvl. Logging messages which are less
#: severe than lvl will be ignored
LOG_LEVEL = logging.INFO

#: Template of string representation of every log of pipeline format
#: see: https://docs.python.org/2/library/logging.html#logrecord-attributes
LOG_FORMAT = "[pipeline-%(levelname)s @ %(asctime)-15s] %(message)s"


PIPELINE_SETUP = "pipeline.pipeline.Pipeline"


#: Database connection string formated ad the URL is an RFC-1738-style string.
#: See: http://docs.sqlalchemy.org/en/latest/core/engines.html
CONNECTION = "sqlite:///pipeline-dev.db"


# Loader class
LOADER = "pipeline.load.Load"


# Pipeline processor steps
STEPS = ["pipeline.steps.MyStep"]


# The alerts
ALERTS = ["pipeline.alerts.MyAlert"]

# This values are autoimported when you open the shell
SHELL_LOCALS = {}


# SMTP server configuration
EMAIL = {
    "server": "",
    "tls": True,
    "user": "",
    "password": ""
}
