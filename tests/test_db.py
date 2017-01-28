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
# DOCS
# =============================================================================

"""All interactions with alembic ans sqlalchemy tests"""


# =============================================================================
# IMPORTS
# =============================================================================

import inspect

import mock

from corral import db, util

from . import models
from .base import BaseTest


# =============================================================================
# BASE CLASS
# =============================================================================

class TestDB(BaseTest):

    def setup(self):
        self.tn2model = {
            sc.__tablename__: sc for sc in util.collect_subclasses(db.Model)}

    def test_models_subsclasess(self):
        actual = [
            v for k, v in vars(models).items()
            if inspect.isclass(v) and
            issubclass(v, db.Model) and not k.startswith("_")]
        actual += [
            v for k, v in vars(db.load_default_models()).items()
            if inspect.isclass(v) and
            issubclass(v, db.Model) and not k.startswith("_")]
        self.assertCountEqual(actual, self.tn2model.values())

    def test_model_module_correctly_imported(self):
        self.assertIs(models, db.load_models_module())

    def test_tables_attributes(self):
        metadata = db.Model.metadata
        for table_name, table in metadata.tables.items():
            model = self.tn2model[table_name]
            self.assertIs(model.__table__, table)

    @mock.patch("corral.db.Model")
    @mock.patch("corral.db.Session")
    @mock.patch("corral.db.engine")
    def test_setup_don_change_engine_model_and_session(self, *args):
        engine, Session, Model = args
        db.setup()
        self.assertIs(db.engine, engine)
        self.assertIs(db.Session, Session)
        self.assertIs(db.Model, Model)

    def tests_create_all(self):
        with mock.patch("corral.db.Model.metadata.create_all") as m_create_all:
            db.create_all()
            self.assertTrue(m_create_all.called)

        with mock.patch("corral.db.Model.metadata.create_all") as m_create_all:
            db.create_all(a=1)
            self.assertTrue(m_create_all.called)
            self.assertEquals(m_create_all.call_args[1], {"a": 1})


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)
