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

from sqlalchemy.orm import object_session

from corral import db, util


class Alerted(db.Model):

    __tablename__ = '__corral_alerted__'

    id = db.Column(db.Integer, primary_key=True)
    alert_path = db.Column(db.String(1000))
    model_table = db.Column(db.String(1000))
    model_ids = db.Column(db.PickleType)
    created_at = db.Column(db.DateTime(timezone=True))

    @classmethod
    def model_class_to_column(cls, mcls):
        table = mcls.__table__
        return {"model_table": table.name}

    @classmethod
    def model_to_columns(cls, m):
        table = m.__table__
        instance_as_dict = m._sa_instance_state.dict
        ids = {
            c: instance_as_dict[c] for c in table.primary_key.columns.keys()}
        columns = cls.model_class_to_column(type(m))
        columns.update({"model_ids": ids})
        return columns

    @classmethod
    def alert_to_columns(cls, alert_cls):
        return {
            "alert_path": ".".join([alert_cls.__module__, alert_cls.__name__])}

    @classmethod
    def all_models(cls):
        if not hasattr(Alerted, "_all_models"):
            Alerted._all_models = {
                cls.__tablename__: cls
                for cls in util.collect_subclasses(db.Model)}
        return Alerted._all_models

    @property
    def model(self):
        if not hasattr(self, "_m"):
            session = object_session(self)
            Model = self.all_models()[self.model_table]
            filters = self.model_ids
            self._m = session.query(Model).filter_by(**filters).first()
        return self._m

    @model.setter
    def model(self, m):
        columns = self.model_to_columns(m)
        self.model_table = columns["model_table"]
        self.model_ids = columns["model_ids"]

    @property
    def alert(self):
        return util.dimport(self.alert_path)

    @alert.setter
    def alert(self, a):
        columns = self.alert_to_columns(a)
        self.alert_path = columns["alert_path"]
