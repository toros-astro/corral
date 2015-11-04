#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# DOC
# =============================================================================

"""All settings tests"""


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

    def setUp(self):
        self.tn2model = {
            sc.__tablename__: sc for sc in util.collect_subclasses(db.Model)}

    def test_models_subsclasess(self):
        actual = [
            v for k, v in vars(models).items()
            if inspect.isclass(v) and issubclass(v, db.Model)
            and not k.startswith("_")]
        self.assertCountEqual(actual, self.tn2model.values())

    def test_model_module_correctly_imported(self):
        self.assertIs(models, db.load_models_module())

    def test_tables_attributes(self):
        metadata = db.Model.metadata
        for table_name, table in metadata.tables.items():
            model = self.tn2model[table_name]
            self.assertIs(model.__table__, table)

    def tests_create_all(self):
        with mock.patch("corral.db.Model.metadata.create_all") as m_create_all:
            db.create_all()
            self.assertTrue(m_create_all.called)

        with mock.patch("corral.db.Model.metadata.create_all") as m_create_all:
            db.create_all(1, 2, 3, a=1)
            self.assertTrue(m_create_all.called)
            self.assertEquals(m_create_all.call_args[0], (1, 2, 3))
            self.assertEquals(m_create_all.call_args[1], {"a": 1})


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)
