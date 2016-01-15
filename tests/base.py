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
        try:
            from corral import util, db
            with db.session_scope() as session:
                for model in util.collect_subclasses(db.Model):
                    session.query(model).delete()
        except:
            pass

    if six.PY2:
        assertRaisesRegex = six.assertRaisesRegex
        assertCountEqual = six.assertCountEqual

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)
