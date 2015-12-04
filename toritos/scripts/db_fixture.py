#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import datetime

from sqlalchemy.orm import sessionmaker
from astropy.io import fits

from corral import db
from corral.conf import settings
from toritos import models


observationsdir = settings.DATA_PATH

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
campaign.observatory_id = macon.id

cameraA = models.CCD()
cameraA.name = 'Azulcito'
cameraA.brand = 'Apogee'
cameraA.model = 'Alta U16'
cameraA.description = 'Camera bought by mario'
cameraA.ypixsize = 4096
cameraA.xpixsize = 4096

campaign.ccd_id = cameraA.id


# -----------------------------------------------------------------------------
# STATES
# -----------------------------------------------------------------------------

rawstate = models.State()
rawstate.name = 'raw_data'
rawstate.folder = settings.PAWPRINT_PATH
rawstate.order = 1
rawstate.is_error = False

cleanedstate = models.State()
cleanedstate.name = 'cleaned_data'
cleanedstate.folder = settings.DATA_PATH
cleanedstate.order = 2
cleanedstate.is_error = False

preprocessed = models.State()
preprocessed.name = 'preprocessed_data'
preprocessed.folder = settings.PREPROCESSED_PATH
preprocessed.order = 3
preprocessed.is_error = False

failed_preprocess = models.State()
failed_preprocess.name = 'failed_to_preprocess'
failed_preprocess.folder = settings.FAILED_PREPROCESS_PATH
failed_preprocess.order = 4
failed_preprocess.is_error = True

astrometried = models.State()
astrometried.name = 'wcs_solved'
astrometried.folder = settings.ASTROMETRIED_PATH
astrometried.order = 5
astrometried.is_error = False

failed_astrometry = models.State()
failed_astrometry.name = 'failed_wcs_solve'
failed_astrometry.folder = settings.FAILED_ASTROMETRIED_PATH
failed_astrometry.order = 6
failed_astrometry.is_error = True

stackstate = models.State()
stackstate.name = 'stack'
stackstate.folder = settings.STACK_PATH
stackstate.order = 7
stackstate.is_error = False

failed_stackstate = models.State()
failed_stackstate.name = 'failed_stack'
failed_stackstate.folder = settings.FAILED_STACK_PATH
failed_stackstate.order = 8
failed_stackstate.is_error = True


# =============================================================================
#
# =============================================================================


session.add(macon)
session.add(campaign)
session.add(cameraA)
session.add(rawstate)
session.add(cleanedstate)
session.add(preprocessed)
session.add(failed_preprocess)
session.add(astrometried)
session.add(failed_astrometry)
session.add(stackstate)
sesson.add(failed_stackstate)

session.commit()


