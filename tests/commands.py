#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

from corral import cli


class TestAPICommand(cli.BaseCommand):

    options = {"title": "foo"}

    def setup(self):
        pass

    def handle(self):
        pass


class TestExitErrorCommand(cli.BaseCommand):
    options = {"title": "exit_error"}

    EXIT_STATUS = random.randint(1, 10000)

    def handle(self):
        self.exit_with(self.EXIT_STATUS)
