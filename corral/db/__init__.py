#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# IMPORTS
# =============================================================================

import sys
from contextlib import contextmanager

from sqlalchemy import *  # noqa
from sqlalchemy.orm import *  # noqa
from sqlalchemy.ext import declarative

from sqlalchemy_utils import *  # noqa

from alembic.config import main as alembic_main

import sadisplay

from .. import conf, util, exceptions


# =============================================================================
# CONSTANTS
# =============================================================================

MODELS_MODULE = "{}.models".format(conf.PACKAGE)

IN_MEMORY_CONNECTIONS = ("sqlite:///:memory:", "sqlite:///")

engine = None

Session = sessionmaker()

Model = declarative.declarative_base(name="Model")


# =============================================================================
# FUNCTIONS
# =============================================================================

def setup(test_connection=False):
    global engine, Session, Model
    if engine:
        return

    conn = get_url(test_connection)

    engine = create_engine(conn, echo=False)
    Session.configure(bind=engine)
    Model.metadata.bind = engine


def get_url(test_connection=False):
    return (
        conf.settings.get("TEST_CONNECTION", "sqlite:///:memory")
        if test_connection else
        conf.settings.CONNECTION)


def load_models_module():
    return util.dimport(MODELS_MODULE)


def load_default_models():
    from . import default_models
    return default_models


def get_models(default=True):
    all_models = util.collect_subclasses(Model)
    models = [
        m for m in vars(load_models_module()).values() if m in all_models]
    if default:
        models.extend(
            m for m in vars(load_default_models()).values() if m in all_models)
    return tuple(models)


def db_exists(connection=None):
    connection = (
        conf.settings.CONNECTION if connection is None else connection)
    real_db = connection not in IN_MEMORY_CONNECTIONS
    return real_db and database_exists(conf.settings.CONNECTION)


def create_all(model_cls=None, **kwargs):
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


def class_diagram(fmt="dot"):
    default_models = load_default_models()

    parsers = {
        "dot": sadisplay.dot,
        "plantuml": sadisplay.plantuml,
    }
    parser = parsers[fmt]

    models = [
        m for m in util.collect_subclasses(Model)
        if sys.modules[m.__module__] != default_models]

    desc = sadisplay.describe(
        models,
        show_methods=True,
        show_properties=True,
        show_indexes=True)

    return parser(desc)


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
