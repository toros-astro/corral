#!/usr/bin/env python
# -*- coding: utf-8 -*-

from corral import run
from corral.conf import settings
from toritos import models, util


class Load(run.Loader):
    def setup(self):
        self.rawstate = self.session.query(models.State).filter(models.State.name == "raw_data").first()
        self.session.autocommit = True

    def generate(self):
        pawprints = util.scandir(settings.PAWPRINTPATH)
        for afile in pawprints:
            data = util.fitsparser(afile)
            print data
            paw = models.Pawprint(**data)
            paw.state_id = self.rawstate.id
            yield paw
