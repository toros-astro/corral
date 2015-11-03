#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Module with simple tools for specific
# toritos data handling routines.

import os
import datetime

from astropy.io import fits

def scandir(path):
    """
    Tool for scanning dirs and returning
    all the fits files located on them.
    """

    for root, dirs, files in os.walk(path):
        for afile in files if '.fit' in afile:
            yield os.path.join(root, afile)


def creation_date(filename):
    t = os.path.getctime(filename)
    return datetime.datetime.fromtimestamp(t)


def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)


def obs_date(obsdate):
    return datetime.datetime.strptime(obsdate,'%Y-%m-%dT%H:%M:%S.%f')

def fitsparser(fitsfile, paw_object):
    """
    Parse a fits file, translating its metadata to column values
    in the paw_object row element, from table pawprint.
    """

    paw_object.modified_at = modification_date(fitsfile)
    paw_object.created_at = creation_time(fitsfile)

    hdr = fits.getheader(fitsfile)

    paw_object.observation_date = obsdate(header['DATE-OBS'])
    paw_object.exptime = header['EXPTIME']
    paw_object.jd = header['JD']
    paw_object.ccdtemp = header['CCD-TEMP']
    paw_object.imagetype = header['IMAGETYP']
    paw_object.xbinning = header['XBINNING']
    paw_object.ybinning = header['YBINNING']
    paw_object.bitpix = header['BITPIX']
    paw_object.simple = header['SIMPLE']
    paw_object.naxis = header['NAXIS']
    paw_object.naxis1 = header['NAXIS1']
    paw_object.naxis2 = header['NAXIS2']
    paw_object.bscale = header['BSCALE']
    paw_object.bzero = header['BZERO']
    paw_object.exposure = header['EXPOSURE']
    paw_object.set_temp = header['SET-TEMP']
    paw_object.xpixsz = header['XPIXSZ']
    paw_object.ypixsz = header['YPIXSZ']
    paw_object.imagetype = header['IMAGETYP']
    paw_object.readoutm = header['READOUTM']
    paw_object.object_ = header['OBJECT']
    paw_object.observer = header['OBSERVER']

    #paw_object.state_id =


    return paw_object
