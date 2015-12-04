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

    def generate(self):
        query = self.session.query(
            models.Pawprint
        ).filter(
            models.Pawprint.state.has(name='cleaned_data'),
            models.Pawprint.imagetype == 'Dark'
        )
        pwps = tuple(query)
        return [pwps]

    def validate(self, pwps):
        assert isinstance(pwps, tuple)

    def process(self, pwps):
        paths = [pwp.get_path() for pwp in pwps]
        darkmaster = util.combineDarks(paths)

        import ipdb; ipdb.set_trace()

