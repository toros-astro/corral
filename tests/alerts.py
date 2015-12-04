#!/usr/bin/env python
# -*- coding: utf-8 -*-

from corral.run import Alert, endpoints as ep

from .models import SampleModel

import six


class Alert1(Alert):

    model = SampleModel
    conditions = [SampleModel.name == "foo"]
    alert_to = [ep.File(six.StringIO())]
