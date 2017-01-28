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
