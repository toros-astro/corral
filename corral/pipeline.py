#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import atexit
import inspect

import six

from . import conf, util, exceptions


# =============================================================================
# CONFIGURATION
# =============================================================================

@six.add_metaclass(abc.ABCMeta)
class PipelineSetup(object):

    @staticmethod
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "__instance"):
            cls.__instance = super(
                PipelineSetup, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    @abc.abstractmethod
    def setup(self):
        pass  # pragma: no cover

    def teardown(self):
        pass


# =============================================================================
# FUNC
# =============================================================================

def load_pipeline_setup():
    import_string = conf.settings.PIPELINE_SETUP
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
