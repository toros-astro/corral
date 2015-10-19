#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import core, db


def run(args):
    core.setup_enviroment()
    db.create_all()
