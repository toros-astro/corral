#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from corral.setup import PipelineSetup
from corral.conf import settings


class TestPipeline(PipelineSetup):

    def logger_conf(self):
        logging.basicConfig(format="[Tests @ %(asctime)-15s] %(message)s")

        level = logging.ERROR

        logging.getLogger("Corral").setLevel(level)

        # http://docs.sqlalchemy.org/en/rel_1_0/core/engines.html
        logging.getLogger('sqlalchemy.engine').setLevel(level)

    def setup(self):
        self.logger_conf()
