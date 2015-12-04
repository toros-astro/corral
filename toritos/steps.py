#!/usr/bin/env python
# -*- coding: utf-8 -*-

from corral import run

import models, util


class StepCleaner(run.Step):

    model = models.Pawprint
    conditions = [model.state.has(name='raw_data')]

    def setup(self):
        self.cleanstate = self.session.query(
            models.State).filter(models.State.name == 'cleaned_data').first()

    def process(self, pwp):
        # Correct imagetype
        correct = util.cleaner('imagetype', pwp.imagetype)
        if correct is not None:
            pwp.imagetype = correct
        # Correct anything you want here

        # Here we change the state of the pawprints
        pwp.state_id = self.cleanstate.id


class StepDarkPreprocess(run.Step):

    model = models.Pawprint
    conditions = [model.state.has(name='raw_data'), model.imagetype == 'Science']
    ordering = [model.id]

    def process(self, pwp):
        path = pwp.get_path()
        print path


#    def validate(self, obj):
#        assert obj.name == "Step1"
