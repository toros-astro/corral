#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created at ${timestamp} by corral ${version}


# =============================================================================
# DOCS
# =============================================================================

"""Global configuration for ${project_name}

"""

# =============================================================================
# CONFIGURATIONS
# =============================================================================

# If debug is in True pipeline sona be much more verbose
DEBUG = True

PIPELINE_SETUP = "${project_name}.pipeline.Pipeline"

# Database connection string
CONNECTION = "sqlite:///${project_name}-dev.db"


# Loader class
LOADER = "${project_name}.load.Load"


# Pipeline processor steps
STEPS = []


# This values are autoimported when you open the shell
SHELL_LOCALS = {}
