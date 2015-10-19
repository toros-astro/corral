#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# IMPORTS
# =============================================================================

import importlib

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext import declarative

from sqlalchemy_utils import *

from . import conf


# =============================================================================
# CONSTANTS
# =============================================================================

MODELS_MODULE = "{}.models".format(conf.PACKAGE)

engine = create_engine(conf.settings.CONNECTION, echo=conf.settings.DEBUG)

Model = declarative.declarative_base(name="Model", bind=engine)


# =============================================================================
# FUNCTIONS
# =============================================================================

def load_models_module():
    return importlib.import_module(MODELS_MODULE)


def create_all(*args, **kwargs):
    return Model.metadata.create_all(*args, **kwargs)

