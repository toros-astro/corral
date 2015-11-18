#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import datetime

from sqlalchemy.orm import sessionmaker
from astropy.io import fits

from corral import db
from toritos import models, local_settings


observationsdir = local_settings.OBSERVATIONSDIR

Session = sessionmaker()
Session.configure(bind=db.engine)

session = Session()

macon = models.Observatory()
macon.name = 'Macon ridge'
macon.latitude = -24.623
macon.longitude = -67.328
macon.description = 'Observatory located in macon ridge'

campaign = models.Campaign()
campaign.name = '2nd run toritos'
campaign.description = 'The second run, after roof failure'
campaign.observatory_id = macon

cameraA = models.CCD()
cameraA.name = 'Azulcito'
cameraA.brand = 'Apogee'
cameraA.model = 'Alta U16'
cameraA.description = 'Camera bought by mario'
cameraA.ypixsize = 4096
cameraA.xpixsize = 4096

campaign.ccd_id = cameraA


# -----------------------------------------------------------------------------
# STATES
# -----------------------------------------------------------------------------

rawstate = models.State()
rawsate.name = "Raw data"
rawstate.folder = local_settings.PAWPRINTPATH
rawstate.order = 1
rawstate.is_error = False

# =============================================================================
#
# =============================================================================


session.add(macon)
session.add(campaign)
session.add(cameraA)

session.commit()


