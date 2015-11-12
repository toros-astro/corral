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

    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, type, value, traceback):
        return self.teardown(type, value, traceback)

    def setup(self):
        pass

    def teardown(self, type, value, traceback):
        pass

    def validate(self, obj):
        if not isinstance(obj, db.Model):
            msg = "{} must be an instance of corral.db.Model"
            raise TypeError(msg.format(obj))

    def save(self, obj):
        self.session.add(obj)

    @abc.abstractmethod
    def generate(self):
        pass  # pragma: no cover

    @property
    def session(self):
        return self.__session


class Loader(_Processor):
    pass


class Step(_Processor):

    model = None
    conditions = None

    ordering = None
    offset, limit = None, None

    def generate(self):
        if self.model is None or self.conditions is None:
            clsname = type(self).__name__
            raise NotImplementedError(
                "'{}' subclass with a default generate must redefine "
                "'model' and 'conditions' class-attributes".format(clsname))
        query = self.session.query(self.model).filter(*self.conditions)
        if self.ordering is not None:
            query = query.order_by(*self.ordering)
        if self.offset is not None:
            query = query.offset(self.offset)
        if self.limit is not None:
            query = query.limit(self.limit)
        return query

    @abc.abstractmethod
    def process(self, obj):
        raise NotImplementedError()  # pragma: no cover


# =============================================================================
# FUNCTIONS
# =============================================================================

def load_loader():
    import_string = conf.settings.LOADER
    cls = util.dimport(import_string)
    if not (inspect.isclass(cls) and issubclass(cls, Loader)):
        msg = "LOADER '{}' must be subclass of 'corral.run.Loader'"
        raise exceptions.ImproperlyConfigured(msg.format(import_string))
    return cls


def load_steps():
    steps = []
    for import_string in conf.settings.STEPS:
        cls = util.dimport(import_string)
        if not (inspect.isclass(cls) and issubclass(cls, Step)):
            msg = "STEP '{}' must be subclass of 'corral.run.Step'"
            raise exceptions.ImproperlyConfigured(msg.format(import_string))
        steps.append(cls)
    return tuple(steps)


def execute_loader(loader_cls):

    if not (inspect.isclass(loader_cls) and issubclass(loader_cls, Loader)):
        msg = "loader_cls '{}' must be subclass of 'corral.run.Loader'"
        raise TypeError(msg.format(loader_cls))

    with db.session_scope() as session, loader_cls(session) as loader:
        generator = loader.generate()
        for obj in (generator or []):
            loader.validate(obj)
            loader.save(obj)


def execute_step(step_cls):
    if not (inspect.isclass(step_cls) and issubclass(step_cls, Step)):
        msg = "step_cls '{}' must be subclass of 'corral.run.Step'"
        raise TypeError(msg.format(step_cls))

    with db.session_scope() as session, step_cls(session) as step:
        for obj in step.generate():
            step.validate(obj)
            generator = step.process(obj) or []
            if not hasattr(generator, "__iter__"):
                generator = (generator,)
            for proc_obj in generator:
                step.validate(proc_obj)
                step.save(proc_obj)
            step.save(obj)
