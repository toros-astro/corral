#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# DOC
# =============================================================================

"""This are the tests for de tests pipeline"""


# =============================================================================
# CLASSES
# =============================================================================


# =============================================================================
# IMPORTS
# =============================================================================

from corral import qa

from . import steps, commands


# =============================================================================
# EXAMPLES
# =============================================================================

class ExampleTestStep1(qa.TestCase):

    subject = steps.Step1

    def setup(self):
        pass

    def validate(self):
        pass


class ExampleTestCommand(qa.TestCase):

    subject = commands.TestAPICommand

    def setup(self):
        pass

    def validate(self):
        pass
