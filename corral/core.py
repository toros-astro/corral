#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import db


def setup_environment():
    db.load_models_module()
