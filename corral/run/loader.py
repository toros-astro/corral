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

import inspect

import six

from .. import db, util, exceptions
from ..core import logger

from .base import Processor, Runner

conf = util.dimport("corral.conf", lazy=True)


# =============================================================================
# LOADER CLASSES
# =============================================================================

class LoaderRunner(Runner):

    def validate_target(self, loader_cls):
        if not (inspect.isclass(loader_cls) and
                issubclass(loader_cls, Loader)):
            msg = "loader_cls '{}' must be subclass of 'corral.run.Loader'"
            raise TypeError(msg.format(loader_cls))

    def run(self):
        loader_cls, proc = self.target, self.current_proc
        logger.info("Executing loader '{}' #{}".format(loader_cls, proc+1))
        with db.session_scope() as session, loader_cls(session, proc) as ldr:
            generator = ldr.generate()
            for obj in (generator or []):
                ldr.validate(obj)
                ldr.save(obj)
        logger.info("Done Loader '{}' #{}".format(loader_cls, proc+1))


class Loader(Processor):

    runner_class = LoaderRunner

    @classmethod
    def retrieve_python_path(cls):
        return conf.settings.LOADER


# =============================================================================
# FUNCTIONS
# =============================================================================

def load_loader():
    logger.debug("Loading Loader Class")
    import_string = conf.settings.LOADER
    cls = util.dimport(import_string)
    if not (inspect.isclass(cls) and issubclass(cls, Loader)):
        msg = "LOADER '{}' must be subclass of 'corral.run.Loader'"
        raise exceptions.ImproperlyConfigured(msg.format(import_string))
    return cls


def execute_loader(loader_cls, sync=False):

    if not (inspect.isclass(loader_cls) and issubclass(loader_cls, Loader)):
        msg = "loader_cls '{}' must be subclass of 'corral.run.Loader'"
        raise TypeError(msg.format(loader_cls))

    procs = []
    loader_cls.class_setup()
    for proc in six.moves.range(loader_cls.get_procno()):
        runner = loader_cls.runner_class()
        runner.setup(loader_cls, proc)
        if sync:
            runner.run()
        else:
            db.engine.dispose()
            runner.start()
        procs.append(runner)
    return tuple(procs)
