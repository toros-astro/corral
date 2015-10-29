#!/usr/bin/env python
# -*- coding: utf-8 -*-

from corral import run


class TestLoader(run.Loader):

    def generate(self):
        pass

class Step1(run.Step):
    def process(self, *args, **kwargs):
        pass

class Step2(run.Step):
    def process(self, *args, **kwargs):
        pass
