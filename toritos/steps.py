#!/usr/bin/env python
# -*- coding: utf-8 -*-

from corral import run

import .models


class StepPreprocess(run.Step):

    model = models.Pawprint
    conditions = [model.state == 'raw_data']  # noqa
    ordering = [model.name]

    def process(self, obj):
        print obj

#    def validate(self, obj):
#        assert obj.name == "Step1"
