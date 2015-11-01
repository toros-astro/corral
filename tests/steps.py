#!/usr/bin/env python
# -*- coding: utf-8 -*-

from corral import run

from .models import SampleModel


class TestLoader(run.Loader):

    def generate(self):
        yield SampleModel(name="foo")


class Step1(run.Step):

    def get_objects(self):
        return self.session.query(
            SampleModel).filter(SampleModel.name == None)  # noqa

    def process(self, obj):
        obj.name = "Step1"


class Step2(run.Step):

    def get_objects(self):
        return self.session.query(SampleModel).filter(
            SampleModel.name == "Step1")

    def process(self, obj):
        obj.name = "Step2"
        return SampleModel(name="foo")
