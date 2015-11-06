#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# IMPORTS
# =============================================================================

from contextlib import contextmanager

from sqlalchemy import *  # noqa
from sqlalchemy.orm import *  # noqa
from sqlalchemy.ext import declarative

from sqlalchemy_utils import *  # noqa

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
    if Model:
        return
    engine = create_engine(conf.settings.CONNECTION, echo=conf.settings.DEBUG)
    Session = sessionmaker(bind=engine)
    Model = declarative.declarative_base(name="Model", bind=engine)


def load_models_module():
    return util.dimport(MODELS_MODULE)


def create_all(model_cls=None, **kwargs):
    cls = moel_cls() if model_cls else Model
    return cls.metadata.create_all(**kwargs)


@contextmanager
def session_scope(session_cls=None):
    """Provide a transactional scope around a series of operations."""
    session = session_cls() if session_cls else Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
