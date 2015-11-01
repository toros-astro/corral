#!/usr/bin/env python
# -*- coding: utf-8 -*-


from corral import cli


class TestAPICommand(cli.BaseCommand):

    options = {
        "title": "foo"}

    @classmethod
    def set_ns(cls, ns, value):
        cls.ns = ns
        cls.value = value

    def setup(self):
        self.ns["setup"] = self.value

    def add_arguments(self, parser):
        self.ns["add_arguments"] = self.value + 1

    def handle(self):
        self.ns["handle"] = self.value + 2
