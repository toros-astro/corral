#!/usr/bin/env python
# -*- coding: utf-8 -*-

from corral import run

import models, util


class StepPawCleaner(run.Step):

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
        util.change_of_state(self.session, pwp, self.cleanstate.id)


class StepCalCleaner(run.Step):

    model = models.CalFile
    conditions = [model.state.has(name='raw_data')]

    def setup(self):
        self.cleanstate = self.session.query(
            models.State).filter(models.State.name == 'cleaned_data').first()

    def process(self, cal):
        # Correct imagetype
        correct = util.cleaner('imagetype', cal.imagetype)
        if correct is not None:
            cal.imagetype = correct
        # Correct anything you want here

        # Here we change the state of the calfiles
        util.change_of_state(self.session, cal, self.cleanstate.id)


class StepDarkPreprocess(run.Step):

    def generate(self):
        query = self.session.query(
            models.CalFile
        ).filter(
            models.CalFile.state.has(name='cleaned_data'),
            models.CalFile.imagetype == 'Dark'
        )
        cals = tuple(query)
        return [cals]

    def validate(self, cals):
        assert isinstance(cals, tuple)

    def process(self, cals):
        metadata = util.meta_dark(cals)

        paths = [cal.get_path() for cal in cals]
        darkmaster = util.combineDarks(paths)
        #darkmaster.header = metadata


