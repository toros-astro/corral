#!/usr/bin/env python
# -*- coding: utf-8 -*-

import atexit
import inspect
import logging

from . import util, exceptions

settings = util.dimport("corral.conf.settings", lazy=True)


# =============================================================================
# CONFIGURATION
# =============================================================================

class PipelineSetup(object):

    name = "Unamed Pipeline"

    @staticmethod
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super(
                PipelineSetup, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def default_setup(self):
        logging.basicConfig(format=settings.LOG_FORMAT)

        level = settings.LOG_LEVEL

        logging.getLogger("Corral").setLevel(level)

        # http://docs.sqlalchemy.org/en/rel_1_0/core/engines.html
        logging.getLogger('sqlalchemy.engine').setLevel(level)
        for k, v in logging.Logger.manager.loggerDict.items():
            if isinstance(v, logging.Logger):
                if k.startswith("alembic"):
                    v.setLevel(level)

    def setup(self):
        self.default_setup()

    def teardown(self):
        pass  # pragma: no cover


# =============================================================================
# FUNC
# =============================================================================

def load_pipeline_setup():
    import_string = settings.PIPELINE_SETUP
    cls = util.dimport(import_string)
    if not (inspect.isclass(cls) and issubclass(cls, PipelineSetup)):
        msg = (
            "PIPELINE_SETUP '{}' must be subclass of "
            "'corral.pipeline.PipelineSetup'").format(import_string)
        raise exceptions.ImproperlyConfigured(msg)
    return cls


def setup_pipeline(setup_cls):
    if not (inspect.isclass(setup_cls) and
            issubclass(setup_cls, PipelineSetup)):
        msg = (
            "PIPELINE_SETUP '{}' must be subclass of "
            "'corral.pipeline.PipelineSetup'").format(setup_cls)
        raise TypeError(msg)
    st = setup_cls()
    st.setup()
    atexit.register(st.teardown)
