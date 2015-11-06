#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# DOC
# =============================================================================

"""All Corral base tests"""


# =============================================================================
# IMPORTS
# =============================================================================

import unittest

import six


# =============================================================================
# BASE CLASS
# =============================================================================

class BaseTest(unittest.TestCase):

    def setup(self):
        pass

    def setUp(self):
        from corral import db
        db.create_all()
        self.setup()

    def teardown(self):
        pass

    def tearDown(self):
        self.teardown()
        from corral import util, db
        with db.session_scope() as session:
            for model in util.collect_subclasses(db.Model):
                session.query(model).delete()

    if six.PY2:
        assertCountEqual = six.assertCountEqual

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)
