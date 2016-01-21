#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created at ${timestamp} by corral ${version}


# =============================================================================
# DOCS
# =============================================================================

"""Global configuration for ${project_name}

"""


# =============================================================================
# IMPORTS
# =============================================================================

import logging
import os


# =============================================================================
# CONFIGURATIONS
# =============================================================================

#: Path where the settings.py lives
PATH = os.path.abspath(os.path.dirname(__file__))

#: Run the steps and alerts with the debug number of processes
DEBUG_PROCESS = True

#: Sets the threshold for this logger to lvl. Logging messages which are less
#: severe than lvl will be ignored
LOG_LEVEL = logging.INFO

#: Template of string representation of every log of ${project_name} format
#: see: https://docs.python.org/2/library/logging.html#logrecord-attributes
LOG_FORMAT = (
        "[${project_name}-%(name)s-%(levelname)s@%(asctime)-15s] %(message)s")


PIPELINE_SETUP = "${project_name}.pipeline.Pipeline"


#: Database connection string formated ad the URL is an RFC-1738-style string.
#: See: http://docs.sqlalchemy.org/en/latest/core/engines.html
CONNECTION = "sqlite:///${project_name}-dev.db"


# Loader class
LOADER = "${project_name}.load.Loader"


# Pipeline processor steps
STEPS = ["${project_name}.steps.MyStep"]


# The alerts
ALERTS = ["${project_name}.alerts.MyAlert"]

# This values are autoimported when you open the shell
SHELL_LOCALS = {}


# SMTP server configuration
EMAIL = {
    "server": "",
    "tls": True,
    "user": "",
    "password": ""
}

MIGRATIONS_SETTINGS = os.path.join(PATH, "migrations", "alembic.ini")
