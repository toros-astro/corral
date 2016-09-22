#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

PATH = os.path.abspath(os.path.dirname(__file__))


def fullpath(fname):
    path = os.path.join(PATH, fname)
    if not os.path.isfile(path):
        raise OSError("Resource '{}' do not exists".format(fname))
    return path
