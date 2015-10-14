#!/usr/bin/env python
# -*- coding: utf-8 -*-

import importlib

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext import declarative

from sqlalchemy_utils import *

from .conf import PACKAGE, settings


MODELS_MODULE = "{}.models".format(PACKAGE)

engine = create_engine(settings.CONNECTION, echo=settings.DEBUG)

Model = declarative.declarative_base(name="Model", bind=engine)


def get_models_module():
    return importlib.import_module(MODELS_MODULE)


def create_all(*args, **kwargs):
    return Model.metadata.create_all(*args, **kwargs)
