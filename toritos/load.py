#!/usr/bin/env python
# -*- coding: utf-8 -*-

from corral import run
from toritos import models, util

class Load(run.Loader):

    def generate(self):
        pawprints = util.scandir(path)
        for afile in pawprints:
            paw = models.Pawprint()
            hdr = fits.getheader(afile)
            paw.exptime = header['EXPTIME']
            paw.jd = header['JD']
            paw.ccdtemp = header['CCD-TEMP']
            paw.imagetype = header['IMAGETYP']
            paw.xbinning = header['XBINNING']
            paw.ybinning = header['YBINNING']
            yield paw
