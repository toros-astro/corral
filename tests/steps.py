#!/usr/bin/env python
# -*- coding: utf-8 -*-

from corral import run

from .models import SampleModel


class TestLoader(run.Loader):

    def generate(self):
        yield SampleModel(name="foo")


class Step1(run.Step):

    model = SampleModel
    conditions = [SampleModel.name == None]  # noqa
    ordering = [SampleModel.name]
    offset = 0
    limit = -1

    def process(self, obj):
        obj.name = "Step1"


class Step2(run.Step):

    model = SampleModel
    conditions = [SampleModel.name == "Step1"]

    def process(self, obj):
        obj.name = "Step2"
        return SampleModel(name="foo")
