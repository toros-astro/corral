#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# DOC
# =============================================================================

"""All Corral base tests"""


# =============================================================================
# IMPORTS
# =============================================================================

from corral import util

from .base import BaseTest


# =============================================================================
# BASE CLASS
# =============================================================================

class TestUtil(BaseTest):

    def test_to_namedtuple(self):
        original = {"x": 1, "y": 2}
        name = "Foo"

        actual = util.to_namedtuple(name, original)
        self.assertEqual(dict(actual._asdict()), original)
        self.assertEqual(actual.__class__.__name__, name)

    def test_collect_subclasses(self):

        class Base(object):
            pass

        class Level1(Base):
            pass

        class Level2(Level1):
            pass

        actual = util.collect_subclasses(Base)
        expected = (Level1, Level2)

        self.assertItemsEqual(actual, expected)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)
