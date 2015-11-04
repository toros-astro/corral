#!/usr/bin/env python
# -*- coding: utf-8 -*-


from corral import cli


class TestAPICommand(cli.BaseCommand):

    options = {
        "title": "foo"}

    def setup(self):
        pass

    def handle(self):
        pass
