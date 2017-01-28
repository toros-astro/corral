#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016-2017, Cabral, Juan; Sanchez, Bruno & Berois, Martín
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# * Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.

# * Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# =============================================================================
# IMPORTS
# =============================================================================

from contextlib import contextmanager

from sqlalchemy import *  # noqa
from sqlalchemy.orm import *  # noqa
from sqlalchemy.ext import declarative
from sqlalchemy.engine import url

from sqlalchemy_utils import *  # noqa

from alembic.config import main as alembic_main

from .. import util, exceptions

conf = util.dimport("corral.conf", lazy=True)


# =============================================================================
# CONSTANTS
# =============================================================================

IN_MEMORY_CONNECTIONS = ("sqlite:///:memory:", "sqlite:///")

engine = None

Session = sessionmaker()  # noqa

Model = declarative.declarative_base(name="Model")


# =============================================================================
# FUNCTIONS
# =============================================================================

def setup(test_connection=False):
    global engine, Session, Model
    if engine:
        return

    conn = get_url(test_connection)

    engine = create_engine(conn, echo=False)  # noqa
    Session.configure(bind=engine)
    Model.metadata.bind = engine


def get_url(test_connection=False):
    return (
        conf.settings.get("TEST_CONNECTION", "sqlite:///:memory")
        if test_connection else
        conf.settings.CONNECTION)


def get_urlo(test_connection=False):
    uri = get_url(test_connection)
    return url.make_url(uri)


def load_models_module():
    MODELS_MODULE = "{}.models".format(conf.PACKAGE)
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
    return real_db and database_exists(conf.settings.CONNECTION)  # noqa


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
