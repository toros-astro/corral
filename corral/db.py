#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# IMPORTS
# =============================================================================

from contextlib import contextmanager

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext import declarative

from sqlalchemy_utils import *

from . import conf, util


# =============================================================================
# CONSTANTS
# =============================================================================

MODELS_MODULE = "{}.models".format(conf.PACKAGE)

engine = None

Session = None

Model = None


# =============================================================================
# FUNCTIONS
# =============================================================================

def setup():
    global engine, Session, Model
    engine = create_engine(conf.settings.CONNECTION, echo=conf.settings.DEBUG)
    Session = sessionmaker(bind=engine)
    Model = declarative.declarative_base(name="Model", bind=engine)


def load_models_module():
    return util.dimport(MODELS_MODULE)


def create_all(*args, **kwargs):
    return Model.metadata.create_all(*args, **kwargs)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
