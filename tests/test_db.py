#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# DOC
# =============================================================================

"""All settings tests"""


# =============================================================================
# IMPORTS
# =============================================================================

import sys
import inspect

from .base import BaseTest

from corral import db, conf, util

from . import models


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
        self.assertItemsEqual(actual, self.tn2model.values())

    def test_model_module_correctly_imported(self):
        self.assertIs(models, db.load_models_module())

    def test_tables_attributes(self):
        metadata = db.Model.metadata
        for table_name, table in metadata.tables.items():
            model = self.tn2model[table_name]
            self.assertIs(model.__table__, table)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)
