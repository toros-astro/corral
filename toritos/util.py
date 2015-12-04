#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Module with simple tools for specific
toritos data handling routines.

"""

import os
import datetime

from astropy.io import fits

from corral.conf import settings

def scandir(path):
    """
    Tool for scanning dirs and returning
    all the fits files located on them.
    """

    for root, dirs, files in os.walk(path):
        for afile in files:
            if os.path.splitext(afile)[-1].lower() in ('.fit', '.fits'):
                #print afile
                yield os.path.join(root, afile)


def creation_date(filename):
    t = os.path.getctime(filename)
    return datetime.datetime.fromtimestamp(t)


def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)


def obs_date(obsdate):
    if obsdate is not None:
        try:
            return datetime.datetime.strptime(obsdate, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            return datetime.datetime.strptime(obsdate, '%Y-%m-%dT%H:%M:%S.%f')



def fitsparser(fitsfile):
    """
    Parse a fits file, translating its metadata to column values
    in the paw_object row element, from table pawprint.
    """

    header = fits.getheader(fitsfile)

    return {
        "observation_date": obs_date(header.get('DATE-OBS')),
        "exptime": header.get('EXPTIME'),
        "jd": header.get('JD'),
        "ccdtemp": header.get('CCD-TEMP'),
        "xbinning": header.get('XBINNING'),
        "ybinning": header.get('YBINNING'),
        "bitpix": header.get('BITPIX'),
        "simple": header.get('SIMPLE'),
        "naxis": header.get('NAXIS'),
        "naxis1": header.get('NAXIS1'),
        "naxis2": header.get('NAXIS2'),
        "bscale": header.get('BSCALE'),
        "bzero": header.get('BZERO'),
        "exposure": header.get('EXPOSURE'),
        "set_temp": header.get('SET-TEMP'),
        "xpixsz": header.get('XPIXSZ'),
        "ypixsz": header.get('YPIXSZ'),
        "imagetype": header.get('IMAGETYP', "unknown"),
        "readoutm": header.get('READOUTM'),
        "object_": header.get('OBJECT'),
        "observer": header.get('OBSERVER'),
        "modified_at": modification_date(fitsfile),
        "created_at": creation_date(fitsfile),
    }

def cleaner(key, value):
    cleaned = settings.CLEANER_ATTR.get(key, {}).get(value)
    return cleaned

