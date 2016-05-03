#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

PATH = os.path.abspath(os.path.dirname(__file__))


def fullpath(fname):
    return os.path.join(PATH, fname)
