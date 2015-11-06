#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc

import six


# =============================================================================
# CLASS
# =============================================================================

@six.add_metaclass(abc.ABCMeta)
class BaseCommand(object):

    @classmethod
    def get_options(cls):
        try:
            return cls.options
        except AttributeError:
            return {}

    def configure(self, parser):
        self.__parser = parser

    def setup(self):
        pass

    def ask(self, question):
        return six.moves.input(question)

    @abc.abstractmethod
    def handle(self, *args, **kwargs):
        pass  # pragma: no cover

    @property
    def parser(self):
        return self.__parser
