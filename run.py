#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


if __name__ == "__main__":
    os.environ.setdefault("CORRAL_SETTINGS_MODULE", "toritos.settings")

    from corral import cli
    cli.run(sys.argv)
