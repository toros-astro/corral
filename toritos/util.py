#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Module with simple tools for specific
toritos data handling routines.

"""

import os
import datetime
import numpy as np

import ccdproc

from astropy.io import fits

from corral.conf import settings

import models

def scandir(path):
    """
    Tool for scanning dirs and returning
    all the fits files located on them.

    Returns a generator, with a path for every file.
    """

    for root, dirs, files in os.walk(path):
        for afile in files:
            if os.path.splitext(afile)[-1].lower() in ('.fit', '.fits'):
                #print afile
                yield os.path.join(root, afile)


def creation_date(filename):
    """Tool for getting the cration time of a file,
    in datetime format.
    """
    t = os.path.getctime(filename)
    return datetime.datetime.fromtimestamp(t)


def modification_date(filename):
    """Tool for getting the modification time of a file,
    in datetime format.
    """
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)


def obs_date(obsdate):
    """Tool for getting the creation time of a file,
    in datetime format.
    """
    if obsdate is not None:
        try:
            return datetime.datetime.strptime(obsdate, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            return datetime.datetime.strptime(obsdate, '%Y-%m-%dT%H:%M:%S.%f')



def fitsparser(fitsfile):
    """
    Parse a fits file, translating its metadata to column values
    in the paw_object row element, from table pawprint.

    Returns a dictionary type object, giving the data present in header
    expressed as key-values for creating a pawprint or calfile table row.
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
    """Tool for healing datarows from pawprints or calfiles,
    it uses the dictionary declared in the settings file, to
    correctly translate values to healed info values.
    """
    cleaned = settings.CLEANER_ATTR.get(key, {}).get(value)
    return cleaned

def combineDarks(darklist):
    """Combine all the dark files into a master dark"""
    darkComb = ccdproc.Combiner([ccdproc.CCDData.read(adark, unit="adu") for adark in darklist])
    darkComb.sigma_clipping(low_thresh=3, high_thresh=3, func=np.ma.median)
    darkmaster = darkComb.average_combine()
    darkmaster.header['exptime'] = fits.getval(darklist[0], 'exptime')
    return darkmaster


def combineBias(biaslist):
    """Combine all the bias files into a master bias"""
    ccdlist = [ccdproc.CCDData.read(abias, unit="adu") for abias in biaslist]
    biasComb = ccdproc.Combiner(ccdlist)
    biasComb.sigma_clipping(low_thresh=3, high_thresh=3, func=np.ma.median)
    biasmaster = biasComb.average_combine()
    return biasmaster


def combineFlats(flatlist, dark=None, bias=None):
    """Combine all flat files into a flat master.
    Subtract dark or bias if provided."""
    ccdflatlist = [ccdproc.CCDData.read(aflat, unit="adu") for aflat in flatlist]
    if dark is not None and bias is None:
        flat_sub = [ccdproc.subtract_dark(aflat, dark, exposure_time='exptime',
            exposure_unit=u.second) for aflat in ccdflatlist]
    elif dark is None and bias is not None:
        flat_sub = [ccdproc.subtract_bias(aflat, bias) for aflat in ccdflatlist]
    else:
        flat_sub = ccdflatlist

    flatComb = ccdproc.Combiner(flat_sub)
    flatComb.sigma_clipping(low_thresh=3, high_thresh=3, func=np.ma.median)
    flatComb.scaling = lambda arr: 1./np.ma.average(arr)
    flatmaster = flatComb.average_combine()
    return flatmaster

def change_of_state(session, pwp, newstate_id):
    """Tool for insert entries in statechanges table
    """
    statechange = models.StateChange()
    statechange.updated_at = datetime.datetime.now()
    statechange.count = pwp.state_count + 1
    pwp.state_count += 1
    statechange.nw_state_id = newstate_id
    statechange.pawprint_id = pwp.id
    statechange.modification_date = modification_date(pwp.get_path())
    pwp.state_id = newstate_id

    session.add(statechange)

def meta_dark(cals):
    metadata = ([], {})
    cals = list(cals)
    exptimesum = 0
    for cal in cals:
        if not cal.ccdtemp > -14.:
            metadata[0].append(cal)
            exptimesum += cal.exptime
        metadata[1]['mean_exptime'] = exptimesum/float(len(metadata[0]))
    return metadata
