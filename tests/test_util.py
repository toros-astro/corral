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

"""All utilities tests"""


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
