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
import datetime
import collections

import six

from .. import db, util, exceptions
from ..db.default_models import Alerted
from ..core import logger

from .base import Processor, Runner

conf = util.dimport("corral.conf", lazy=True)


# =============================================================================
# CONSTANTS
# =============================================================================

ALERT_TEMPLATE = (
    "[{project_name}-ALERT @ {now}-15s] Check the object '{obj}'\n")


# =============================================================================
# ALERT CLASSES
# =============================================================================

class AlertRunner(Runner):

    def validate_target(self, alert_cls):
        if not (inspect.isclass(alert_cls) and issubclass(alert_cls, Alert)):
            msg = "alert_cls '{}' must be subclass of 'corral.run.Alert'"
            raise TypeError(msg.format(alert_cls))

    def run(self):
        alert_cls, proc = self.target, self.current_proc
        logger.info("Executing alert '{}' #{}".format(alert_cls, proc+1))
        with db.session_scope() as session, alert_cls(session, proc) as alert:
            for obj in alert.generate():
                alert.validate(obj)

                generator = alert.process(obj) or []
                if not hasattr(generator, "__iter__"):
                    generator = (generator,)
                for proc_obj in generator:
                    alert.validate(proc_obj)
                    alert.save(proc_obj)
        logger.info("Done Alert '{}' #{}".format(alert_cls, proc+1))


class Alert(Processor):

    runner_class = AlertRunner

    model = None
    conditions = None

    ordering = None
    offset, limit = None, None

    auto_register = True

    @classmethod
    def retrieve_python_path(cls):
        for import_string in conf.settings.ALERTS:
            if cls == util.dimport(import_string):
                return import_string

    def setup(self):
        for ep in self.alert_to:
            ep.setup(self)

    def teardown(self, type, value, traceback):
        for ep in self.alert_to:
            ep.teardown(type, value, traceback)

    def generate(self):
        if self.model is None or self.conditions is None:
            clsname = type(self).__name__
            raise NotImplementedError(
                "'{}' subclass with a default generate must redefine "
                "'model' and 'conditions' class-attributes".format(clsname))

        query = self.session.query(self.model).filter(*self.conditions)

        if self.auto_register:
            query = self._filter_auto_registered(query)
        else:
            query = self.filter_registered(query)

        if self.ordering is not None:
            query = query.order_by(*self.ordering)
        if self.offset is not None:
            query = query.offset(self.offset)
        if self.limit is not None:
            query = query.limit(self.limit)
        return query

    def _filter_auto_registered(self, query):
        filters = Alerted.alert_to_columns(type(self))
        filters.update(Alerted.model_class_to_column(self.model))
        alerteds = self.session.query(Alerted.model_ids).filter_by(**filters)
        if alerteds.count():
            grouped_id = collections.defaultdict(set)
            for row in alerteds.all():
                for k, v in six.iteritems(row[0]):
                    grouped_id[k].add(v)
            exclude = []
            for k, v in grouped_id.items():
                exclude.append(getattr(self.model, k).in_(v))
            query = query.filter(~db.and_(*exclude))
        return query

    def _auto_register(self, obj):
        register = Alerted()
        register.alert = type(self)
        register.model = obj
        register.created_at = datetime.datetime.utcnow()
        return register

    def filter_registered(self, query):
        raise NotImplementedError()

    def register(self, obj):
        raise NotImplementedError()

    def process(self, obj):
        for ep in self.alert_to:
            ep.process(obj)
        if self.auto_register:
            return self._auto_register(obj)
        else:
            return self.register(obj)

    def render_alert(self, utcnow, endpoint, obj):
        return ALERT_TEMPLATE.format(
            project_name=conf.PACKAGE, now=utcnow.isoformat(), obj=obj)


# =============================================================================
# FUNCTIONS
# =============================================================================

def alerts_groups():
    groups = set()
    for cls in load_alerts():
        groups.update(cls.get_groups())
    return tuple(sorted(groups))


def load_alerts(groups=None):
    alerts = []
    logger.debug("Loading Alert Classes")
    for import_string in conf.settings.ALERTS:
        cls = util.dimport(import_string)
        if not (inspect.isclass(cls) and issubclass(cls, Alert)):
            msg = "STEP '{}' must be subclass of 'corral.run.Alert'"
            raise exceptions.ImproperlyConfigured(msg.format(import_string))
        if groups is None or set(cls.get_groups()).intersection(groups):
            alerts.append(cls)
    alerts.sort(key=lambda cls: cls.__name__)
    return tuple(alerts)


def execute_alert(alert_cls, sync=False):
    if not (inspect.isclass(alert_cls) and issubclass(alert_cls, Alert)):
        msg = "alert_cls '{}' must be subclass of 'corral.run.Alert'"
        raise TypeError(msg.format(alert_cls))
    procs = []
    alert_cls.class_setup()
    for proc in six.moves.range(alert_cls.get_procno()):
        runner = alert_cls.runner_class()
        runner.setup(alert_cls, proc)
        if sync:
            runner.run()
        else:
            db.engine.dispose()
            runner.start()
        procs.append(runner)
    return tuple(procs)
