#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import db


def setup_enviroment():
    db.load_models_module()
