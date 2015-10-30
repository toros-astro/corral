#!/usr/bin/env python
# -*- coding: utf-8 -*-

from corral import run

from . import models


class TestLoader(run.Loader):

    def generate(self):
        yield models.SampleModel(name="foo")


class Step1(run.Step):
    def process(self, *args, **kwargs):
        pass

class Step2(run.Step):
    def process(self, *args, **kwargs):
        pass
