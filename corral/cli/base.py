#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc

import six


# =============================================================================
# CLASS
# =============================================================================

@six.add_metaclass(abc.ABCMeta)
class BaseCommand(object):

    def __init__(self, parser):
        self.parser = parser

    def setup(self):
        pass

    def ask(self, question):
        return six.moves.input(question)

    @abc.abstractmethod
    def handle(self, *args, **kwargs):
        raise NotImplementedError()
