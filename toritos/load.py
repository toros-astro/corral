#!/usr/bin/env python
# -*- coding: utf-8 -*-

from corral import run
from toritos import models

class Load(run.Loader):

    def generate(self):
        for afile in pawprints:
            paw = models.Pawprint()
            hdr = fits.getheader(afile)
            yield paw
