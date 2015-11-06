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

import mock

from .base import BaseTest


# =============================================================================
# BASE CLASS
# =============================================================================

class ToNamedTuple(BaseTest):

    def test_to_namedtuple(self):
        original = {"x": 1, "y": 2}
        name = "Foo"

        actual = util.to_namedtuple(name, original)
        self.assertEqual(dict(actual._asdict()), original)
        self.assertEqual(actual.__class__.__name__, name)


class CollectSubclasses(BaseTest):

    def test_collect_subclasses(self):

        class Base(object):
            pass

        class Level1(Base):
            pass

        class Level2(Level1):
            pass

        actual = util.collect_subclasses(Base)
        expected = (Level1, Level2)

        self.assertCountEqual(actual, expected)


class DImport(BaseTest):

    def test_dimport(self):
        import os
        actual = util.dimport("os")
        self.assertEqual(actual, os)

        actual = util.dimport("os.path")
        self.assertEqual(actual, os.path)

        actual = util.dimport("os.open")
        self.assertEqual(actual, os.open)

        with self.assertRaises(ImportError):
            util.dimport("foo")

    @mock.patch("importlib.import_module",
                side_effect=ImportError("No module named foo"))
    def test_import_file_with_dead_dependency_show_correct_message(self, ipl):
        # https://github.com/toros-astro/corral/issues/11
        with self.assertRaisesRegex(ImportError, "No module named foo"):
            util.dimport("faa")



# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)
