#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Toritos global settings

"""


import logging

import numpy as np



LOG_LEVEL = logging.INFO

LOG_FORMAT = "[Toritos-%(levelname)s @ %(asctime)-15s] %(message)s"

CONNECTION = 'sqlite:///toritos-dev.db'

LOADER = "toritos.load.Load"

PIPELINE_SETUP = "toritos.pipeline.Toritos"

STEPS = ["toritos.steps.StepCleaner", "toritos.steps.StepDarkPreprocess"]

PAWPRINTPATH = " "

# This values are autoimported when you open the shell
SHELL_LOCALS = {
    "np": np
}


CLEANER_ATTR = {
    'imagetype': {
        'zero': 'Bias',
        'bias': 'Bias',
        'dark': 'Dark',
        'DARK': 'Dark',
        'FLAT': 'Flat',
        'Light Frame': 'Science',
        'object': 'Science',
        'flat': 'Flat',
        'flatdome': 'Flat',
        'skyflat': 'Flat',
        'LIGHT': 'Science',
        'Flat Frame': 'Flat',
        'Dark Frame': 'Dark',
        'Bias Frame': 'Bias'
    }
}



try:
    from .local_settings import *  # noqa
except ImportError:
    pass

