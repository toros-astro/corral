#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016-2017, Cabral, Juan; Sanchez, Bruno & Berois, Martín
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# * Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.

# * Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# =============================================================================
# IMPORTS
# =============================================================================

import abc
import multiprocessing

import six

from .. import db, util

conf = util.dimport("corral.conf", lazy=True)


# =============================================================================
# ABSTRACT CLASS
# =============================================================================

@six.add_metaclass(abc.ABCMeta)
class Processor(object):

    runner_class = None
    procno = 1
    groups = ["default"]

    @classmethod
    def class_setup(cls):
        pass

    @classmethod
    def get_groups(cls):
        return cls.groups

    @classmethod
    def get_procno(cls):
        if conf.settings.DEBUG_PROCESS:
            return cls.procno
        return getattr(cls, "production_procno", cls.procno)

    @classmethod
    def retrieve_python_path(cls):
        return cls.__name__

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

    def delete(self, obj):
        if isinstance(obj, db.Model):
            self.session.delete(obj)

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
