#!/usr/bin/env python
# -*- coding: utf-8 -*-

from corral.run import Alert, endpoints as ep

from .models import SampleModel


class Alert1(Alert):

    model = SampleModel
    conditions = [SampleModel.name == "catch_alert"]
    ordering = [SampleModel.name]
    offset = 0
    limit = -1
    alert_to = [ep.File(":memory:")]

    def render_alert(self, utcnow, endpoint, obj):
        return obj.name
