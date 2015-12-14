#!/usr/bin/env python
# -*- coding: utf-8 -*-

from corral import run
from corral.conf import settings
from . import models, util


class Load(run.Loader):
    def setup(self):
        self.rawstate = self.session.query(
            models.State).filter(models.State.name == 'raw_data').first()
        self.session.autocommit = False
        self.buff = []

    def generate(self):
        pawprints = util.scandir(settings.PAWPRINT_PATH)
        for afile in pawprints:
            data = util.fitsparser(afile)
            cleaned = util.cleaner('imagetype', data['imagetype'])
            if cleaned == 'Science':
                paw = models.Pawprint(**data)
                paw.state_count = 0
                paw.state_id = self.rawstate.id
                self.buff.append((afile, paw))
                yield paw
            else:
                cal = models.CalFile(**data)
                cal.state_count = 0
                cal.state_id = self.rawstate.id
                self.buff.append((afile, cal))
                yield cal

    def teardown(self, type, value, traceback):
        if not type:
            self.session.commit()
            for afile, row in self.buff:
                row.writefile(afile, self.rawstate)
