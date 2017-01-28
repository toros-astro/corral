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
# DOC
# =============================================================================

"""All piple creation subrutines tests"""


# =============================================================================
# IMPORTS
# =============================================================================

import tempfile
import shutil
import os

from corral import creator
from corral.exceptions import ValidationError

from .base import BaseTest


# =============================================================================
# BASE CLASS
# =============================================================================

class ValidateName(BaseTest):

    def test_validate_name(self):
        creator.validate_name("fooo")
        creator.validate_name("_fooo")
        creator.validate_name("fooo111")

        with self.assertRaises(ValidationError):
            creator.validate_name("try")
        with self.assertRaises(ValidationError):
            creator.validate_name("import")

        with self.assertRaises(ValidationError):
            creator.validate_name("corral")
        with self.assertRaises(ValidationError):
            creator.validate_name("True")

        with self.assertRaises(ValidationError):
            creator.validate_name("models")

        with self.assertRaises(ValidationError):
            creator.validate_name("int")

        with self.assertRaises(ValidationError):
            creator.validate_name("1a")

        with self.assertRaises(ValidationError):
            creator.validate_name("pipeline")

        with self.assertRaises(ValidationError):
            creator.validate_name("load")


class CreatePipeline(BaseTest):

    def setup(self):
        self.path = tempfile.mkdtemp("_corral_tests")
        self.pipeline_name = "example"
        self.pipeline_path = os.path.join(self.path, self.pipeline_name)
        self.container_path = os.path.join(self.path, self.pipeline_name)

    def teardown(self):
        if os.path.isdir(self.path):
            shutil.rmtree(self.path)

    def test_create_pipeline(self):
        self.assertEqual(os.listdir(self.path), [])

        creator.create_pipeline(self.pipeline_path)

        expected = ['in_corral.py', 'example']
        self.assertCountEqual(os.listdir(self.container_path), expected)

        self.assertTrue(os.path.isdir(self.pipeline_path))

        manager_path = os.path.join(self.container_path, "in_corral.py")
        self.assertTrue(os.path.isfile(manager_path))

    def test_directory_exists_failure(self):
        with self.assertRaises(ValidationError):
            creator.create_pipeline(self.path)
