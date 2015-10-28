#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import inspect

import six

from . import conf, db, util, exceptions


# =============================================================================
# CLASSESS
# =============================================================================

@six.add_metaclass(abc.ABCMeta)
class _Processor(object):

    def __init__(self, session):
        self.__session = session

    def setup(self):
        pass

    @property
    def session(self):
        return self.__session

    def teardown(self):
        pass


class Loader(_Processor):

    @property
    def generate(self):
        pass


class Step(_Processor):

    def get_queryset(self):
        pass

    @abc.abstractmethod
    def process(self, *args, **kwargs):
        raise NotImplementedError()

    def validate(self, **kwargs):
        pass


# =============================================================================
# FUNCTIONS
# =============================================================================

def load_loader():
    import_string = conf.settings.LOADER
    cls = util.dimport(import_string)
    if not (inspect.isclass(cls) and issubclass(cls, Loader)):
        msg = "LOADER '{}' must be subclass of 'corral.steps.Loader'"
        raise exceptions.ImproperlyConfigured(msg.format(import_string))
    return cls


def load_steps():
    pass


def execute_step(step_cls):
    pass


def execute_loader(loader_cls):
    pass


def execute_steps(steps_clss):
    pass




