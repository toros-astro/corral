#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# DOC
# =============================================================================

"""All settings tests"""


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
        self.pipeline_path = os.path.join(self.path, "example")

    def teardown(self):
        if os.path.isdir(self.path):
            shutil.rmtree(self.path)

    def test_create_pipeline(self):
        self.assertEqual(os.listdir(self.path), [])

        creator.create_pipeline(self.pipeline_path)

        expected = ['in_corral.py', 'example']
        self.assertCountEqual(os.listdir(self.path), expected)

        self.assertTrue(os.path.isdir(self.pipeline_path))

        manager_path = os.path.join(self.path, "in_corral.py")
        self.assertTrue(os.path.isfile(manager_path))

        template_basenames = [
            e for e, _ in creator.TEMPLATES if e != "in_corral.py"]
        self.assertCountEqual(
            os.listdir(self.pipeline_path), template_basenames)

    def test_directory_exists_failure(self):
        with self.assertRaises(ValidationError):
            creator.create_pipeline(self.path)
