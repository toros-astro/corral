#!/usr/bin/env python
# -*- coding: utf-8 -*-

from corral import run

import models

class StepPreprocess(run.Step):

    model = models.Pawprint
    conditions = [model.state.has(name='raw')]
    ordering = [model.id]

    def process(self, pwp):
        path = pwp.get_path()


#    def validate(self, obj):
#        assert obj.name == "Step1"
