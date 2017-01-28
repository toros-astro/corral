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

"""All reporting tests"""


# =============================================================================
# IMPORTS
# =============================================================================

import mock

from corral import setup, exceptions

from .base import BaseTest
from .pipeline import TestPipeline


# =============================================================================
# BASE CLASS
# =============================================================================

class LoadSetupTests(BaseTest):

    def test_load_setup(self):
        actual = setup.load_pipeline_setup()
        self.assertIs(actual, TestPipeline)

    def test_always_the_same(self):
        self.assertIs(TestPipeline(), TestPipeline())
        self.assertIs(TestPipeline(), setup.load_pipeline_setup()())
        self.assertIs(setup.load_pipeline_setup()(),
                      setup.load_pipeline_setup()())

    def test_load_setup_fail(self):
        with mock.patch("corral.conf.settings.PIPELINE_SETUP", new="os.open"):
            with self.assertRaises(exceptions.ImproperlyConfigured):
                setup.load_pipeline_setup()


class SetupTests(BaseTest):

    def test_setup_pipeline(self):
        with mock.patch("atexit.register") as register:
            with mock.patch.object(TestPipeline, "setup") as pipeline_setup:
                setup.setup_pipeline(TestPipeline)
                self.assertTrue(pipeline_setup.called)
                register.assert_called_with(TestPipeline().teardown)

    def test_setup_pipeline_fail(self):
        with self.assertRaises(TypeError):
            setup.setup_pipeline(None)
