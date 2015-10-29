#!/usr/bin/env python
# -*- coding: utf-8 -*-

from corral import run
from toritos import models

class Load(run.Loader):

    def generate(self):
        macon = models.Observatory()
        macon.name = 'Macon ridge'
        macon.latitude = -24.623
        macon.longitude = -67.328
        macon.description = 'Observatory located in macon ridge'
        yield macon


