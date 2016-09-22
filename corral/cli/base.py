#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc

import six

# =============================================================================
# CONSTANTS
# =============================================================================

MODE_IN, MODE_TEST, MODE_OUT = "in", "test", "out"


# =============================================================================
# CLASS
# =============================================================================

@six.add_metaclass(abc.ABCMeta)
class BaseCommand(object):

    @classmethod
    def get_options(cls):
        try:
            options = cls.options
        except AttributeError:
            options = {}
        options.setdefault("title", cls.__name__.lower())
        options.setdefault("mode", MODE_IN)
        options.setdefault("description", cls.__doc__ or "")
        return options

    def __init__(self):
        self.__exit_status = 0

    def exit_with(self, v):
        self.__exit_status = int(v)

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

    @property
    def exit_status(self):
        return self.__exit_status
