#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import db

def run(args):
    db.get_models_module()
    db.create_all()
