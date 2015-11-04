#!/usr/bin/env python
# -*- coding: utf-8 -*-

from corral import run
from corral.conf import settings
from toritos import models, util


class Load(run.Loader):
    def setup(self):
        self.session.autocommit = True

    def generate(self):
        pawprints = util.scandir(settings.PAWPRINTPATH)
        for afile in pawprints:
            data = util.fitsparser(afile)
            print data
            paw = models.Pawprint(**data)
            yield paw
