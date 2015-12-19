#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import multiprocessing

import six

from .. import db


# =============================================================================
# ABSTRACT CLASS
# =============================================================================

@six.add_metaclass(abc.ABCMeta)
class Processor(object):

    runner_class = None
    procno = 1

    @classmethod
    def class_setup(cls):
        pass

    def __init__(self, session, proc):
        self.__session = session
        self.__current_proc = proc

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
        if isinstance(obj, db.Model):
            self.session.add(obj)

    @abc.abstractmethod
    def generate(self):
        raise NotImplementedError  # pragma: no cover

    @property
    def session(self):
        return self.__session

    @property
    def current_proc(self):
        return self.__current_proc


@six.add_metaclass(abc.ABCMeta)
class Runner(multiprocessing.Process):

    @abc.abstractmethod
    def validate_target(self, target):
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError  # pragma: no cover

    def setup(self, target, proc):
        self.validate_target(target)
        self.target = target
        self.current_proc = proc
