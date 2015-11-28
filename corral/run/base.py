#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc

import six

from .. import db


# =============================================================================
# ABSTRACT CLASS
# =============================================================================

@six.add_metaclass(abc.ABCMeta)
class Processor(object):

    runner_class = None

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
        raise NotImplementedError  # pragma: no cover

    @property
    def session(self):
        return self.__session


@six.add_metaclass(abc.ABCMeta)
class Runner(object):

    @abc.abstractmethod
    def setup(self, *args, **kwargs):
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError  # pragma: no cover
