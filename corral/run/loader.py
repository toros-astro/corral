#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
import multiprocessing

from .. import conf, db, util, exceptions
from ..core import logger

from .base import Processor, Runner


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
        loader_cls = self.target
        logger.info("Executing loader '{}'".format(loader_cls))
        with db.session_scope() as session, loader_cls(session) as loader:
            generator = loader.generate()
            for obj in (generator or []):
                loader.validate(obj)
                loader.save(obj)
        logger.info("Done!")



class Loader(Processor):

    runner_class = LoaderRunner


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

    runner = loader_cls.runner_class()
    runner.set_target(loader_cls)
    if sync:
        runner.run()
    else:
        runner.start()
    return runner
