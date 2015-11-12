#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Toritos global settings

"""

import numpy as np

DEBUG = True

LOGGER_FORMAT = "[Toritos-%(levelname)s @ %(asctime)-15s] %(message)s"

CONNECTION = 'sqlite:///toritos-dev.db'

LOADER = "toritos.load.Load"

PIPELINE_SETUP = "toritos.pipeline.Toritos"

STEPS = []

PAWPRINTPATH = " "

# This values are autoimported when you open the shell
SHELL_LOCALS = {
    "np": np
}

try:
    from .local_settings import *  # noqa
except ImportError:
    pass
