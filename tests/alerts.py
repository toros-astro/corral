#!/usr/bin/env python
# -*- coding: utf-8 -*-

from corral.run import Alert, endpoints as ep

from .models import SampleModel


class Alert1(Alert):

    model = SampleModel
    conditions = [SampleModel.name == "foo"]
    alert_to = [ep.Email(["example@example.com"])]
