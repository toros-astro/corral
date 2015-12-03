#!/usr/bin/env python
# -*- coding: utf-8 -*-

from corral import db


class Alerted(db.Model):

    __tablename__ = '__corral_alerted__'

    id = db.Column(db.Integer, primary_key=True)
    model_table = db.Column(db.Text, nullable=True)
    model_id_type = db.Column(db.Text, nullable=True)
    model_id = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True))

    def __repr__(self):
        return "<Alerted '{}'>".format(self.model)

    @property
    def model(self):
        pass

    @model.setter
    def model(self, m):
        import ipdb; ipdb.set_trace()

