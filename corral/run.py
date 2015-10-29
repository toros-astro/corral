#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import inspect

import sqlalchemy.orm

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

    @abc.abstractmethod
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
    steps = []
    for import_string in conf.settings.STEPS:
        cls = util.dimport(import_string)
        if not (inspect.isclass(cls) and issubclass(cls, Step)):
            msg = "STEP '{}' must be subclass of 'corral.steps.Step'"
            raise exceptions.ImproperlyConfigured(msg.format(import_string))
        steps.append(cls)
    return tuple(steps)


def execute_step(step_cls):
    pass


def execute_loader(loader_cls):
    if not (inspect.isclass(loader_cls) and issubclass(loader_cls, Loader)):
        msg = "loader_cls '{}' must be subclass of 'corral.steps.Loader'"
        raise TypeError(msg.format(loader_cls))
    with db.session_scope() as session:
        loader = loader_cls(session)
        loader.setup()
        try:
            for obj in loader.generate():
                if not isinstance(obj, db.Model):
                    msg = "{} must be an instance of corral.db.Model"
                    raise TypeError(msg.format(obj))
                session.add(obj)
        finally:
            loader.teardown()


def execute_steps(steps_cls):
    pass




