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
import inspect

import six

from .. import db, util, exceptions
from ..core import logger

from .base import Processor, Runner

conf = util.dimport("corral.conf", lazy=True)


# =============================================================================
# STEP CLASSES
# =============================================================================

class StepRunner(Runner):

    def validate_target(self, step_cls):
        if not (inspect.isclass(step_cls) and issubclass(step_cls, Step)):
            msg = "step_cls '{}' must be subclass of 'corral.run.Step'"
            raise TypeError(msg.format(step_cls))

    def run(self):
        step_cls, proc = self.target, self.current_proc
        logger.info("Executing step '{}' #{}".format(step_cls, proc+1))
        with db.session_scope() as session, step_cls(session, proc) as step:
            for obj in step.generate():
                step.validate(obj)
                generator = step.process(obj) or []
                if not hasattr(generator, "__iter__"):
                    generator = (generator,)
                for proc_obj in generator:
                    step.validate(proc_obj)
                    step.save(proc_obj)
                step.save(obj)
        logger.info("Done Step '{}' #{}".format(step_cls, proc+1))


class Step(Processor):

    runner_class = StepRunner

    model = None
    conditions = None

    ordering = None
    offset, limit = None, None

    @classmethod
    def retrieve_python_path(cls):
        for import_string in conf.settings.STEPS:
            if cls == util.dimport(import_string):
                return import_string

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

def steps_groups():
    groups = set()
    for cls in load_steps():
        groups.update(cls.get_groups())
    return tuple(sorted(groups))


def load_steps(groups=None):
    steps = []
    logger.debug("Loading Steps Classes")
    for import_string in conf.settings.STEPS:
        cls = util.dimport(import_string)
        if not (inspect.isclass(cls) and issubclass(cls, Step)):
            msg = "STEP '{}' must be subclass of 'corral.run.Step'"
            raise exceptions.ImproperlyConfigured(msg.format(import_string))
        if groups is None or set(cls.get_groups()).intersection(groups):
            steps.append(cls)
    steps.sort(key=lambda cls: cls.__name__)
    return tuple(steps)


def execute_step(step_cls, sync=False):
    if not (inspect.isclass(step_cls) and issubclass(step_cls, Step)):
        msg = "step_cls '{}' must be subclass of 'corral.run.Step'"
        raise TypeError(msg.format(step_cls))

    procs = []
    step_cls.class_setup()
    for proc in six.moves.range(step_cls.get_procno()):
        runner = step_cls.runner_class()
        runner.setup(step_cls, proc)
        if sync:
            runner.run()
        else:
            db.engine.dispose()
            runner.start()
        procs.append(runner)
    return tuple(procs)
