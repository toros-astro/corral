#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created at ${timestamp} by corral ${version}


# =============================================================================
# DOCS
# =============================================================================

"""${project_name} steps

"""


# =============================================================================
# IMPORTS
# =============================================================================

from corral import run

# from . import models


# =============================================================================
# STEPS
# =============================================================================

class MyStep(run.Step):

    model = None
    conditions = []

    def process(self, obj):
        # your logic here
        pass
