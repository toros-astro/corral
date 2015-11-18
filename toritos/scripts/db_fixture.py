#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import datetime

from sqlalchemy.orm import sessionmaker
from astropy.io import fits

from corral import db, settings
from toritos import models


observationsdir = settings.OBSERVATIONSDIR

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
rawstate.name = 'Raw data'
rawstate.folder = settings.PAWPRINTPATH
rawstate.order = 1
rawstate.is_error = False

preprocessed = models.State()
preprocessed.name = 'Preprocessed data'
preprocessed.folder = settings.PREPROCESSED_PATH
preprocessed.order = 2
preprocessed.is_error = False

failed_preprocess = models.State()
failed_preprocess.name = 'Failed to preprocess'
failed_preprocess.folder = settings.FAILED_PREPROCESS_PATH
failed_preprocess.order = 3
failed_preprocess.is_error = True

astrometried = models.State()
astrometried.name = 'WCS astrometry solved'
astrometried.folder = settins.ASTROMETRIED_PATH
astrometried.order = 4
astrometried.is_error = False

failed_astrometry = models.State()
failed_astrometry.name = 'Failed to solve WCS astrometry'
failed_astrometry.folder = settings.FAILED_ASTROMETRIED_PATH
failed_astrometry.order = 5
failed_astrometry.is_error = True


# =============================================================================
#
# =============================================================================


session.add(macon)
session.add(campaign)
session.add(cameraA)

session.commit()


