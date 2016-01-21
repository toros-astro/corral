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

from alembic.config import main as alembic_main

from .. import conf, util, exceptions


# =============================================================================
# CONSTANTS
# =============================================================================

MODELS_MODULE = "{}.models".format(conf.PACKAGE)

IN_MEMORY_CONNECTIONS = ("sqlite:///:memory:", "sqlite:///")

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
    engine = create_engine(conf.settings.CONNECTION, echo=False)
    Session = sessionmaker(bind=engine)
    Model = declarative.declarative_base(name="Model", bind=engine)


def load_models_module():
    return util.dimport(MODELS_MODULE)


def load_default_models():
    from . import default_models
    return default_models


def db_exists(connection=None):
    connection = (
        conf.settings.CONNECTION if connection is None else connection)
    real_db = connection not in IN_MEMORY_CONNECTIONS
    return real_db and database_exists(conf.settings.CONNECTION)


def create_all(model_cls=None, **kwargs):
    if db_exists():
        raise exceptions.DBError("Database already exists")
    cls = model_cls() if model_cls else Model
    return cls.metadata.create_all(**kwargs)


def alembic(*args):
    if not db_exists():
        raise exceptions.DBError("Database do not exists")
    aargs = ["--config", conf.settings.MIGRATIONS_SETTINGS] + list(args)
    return alembic_main(aargs, "corral")


def makemigrations(message=None):
    args = ("-m", message) if message else ()
    return alembic("revision", "--autogenerate", *args)


def migrate():
    return alembic("upgrade", "head")


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
