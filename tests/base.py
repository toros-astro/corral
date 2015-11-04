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

    def tearDown(self):
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
