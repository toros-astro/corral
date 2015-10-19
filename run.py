#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

os.environ.setdefault("CORRAL_SETTINGS_MODULE", "toritos.settings")

from corral import cli
cli.run_from_command_line(sys.argv[1:])
