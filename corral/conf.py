#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import importlib

CORRAL_SETTINGS_MODULE = os.environ["CORRAL_SETTINGS_MODULE"]

PACKAGE = CORRAL_SETTINGS_MODULE.split(".", 1)[0]

settings = importlib.import_module(CORRAL_SETTINGS_MODULE)


