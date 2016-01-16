#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
