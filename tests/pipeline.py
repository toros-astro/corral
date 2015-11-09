#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from corral.pipeline import PipelineSetup
from corral.conf import settings


class Test(PipelineSetup):

    def logger_conf(self):
        logging.basicConfig(format="[Tests @ %(asctime)-15s] %(message)s")

        level = logging.INFO if settings.DEBUG else logging.WARNING

        logging.getLogger("Corral").setLevel(level)

        # http://docs.sqlalchemy.org/en/rel_1_0/core/engines.html
        logging.getLogger('sqlalchemy.engine').setLevel(level)

    def setup(self):
        self.logger_conf()
