#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created at ${timestamp} by corral ${version}


# =============================================================================
# DOCS
# =============================================================================

"""${project_name} alerts

"""


# =============================================================================
# IMPORTS
# =============================================================================

from corral import run
from corral.run import endpoints as ep

# from . import models


# =============================================================================
# ALERTS
# =============================================================================

class MyAlert(run.Alert):

    model = None
    conditions = []
    alert_to = [ep.File("my_alert.log")]