#!/usr/bin/env python
# -*- coding: utf-8 -*-

from corral import db


class Observatory(db.Model):

    __tablename__ = 'Observatory'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)

    def repr(self):
        return self.name


class CCD(db.Model):

    __tablename__ = 'CCD'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    brand = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return self.name


class Campaign(db.Model):

    __tablename__ = 'Campaign'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)

    observatory = db.relationship(
        "Observatory", backref=db.backref('campaigns', order_by=id))
    ccd = db.relationship(
        "CCD", backref=db.backref('campaigns', order_by=id))

    def repr(self):
        return self.name


class State(db.Model):

    __tablename__ = 'State'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    folder = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, nullable=False)
    is_error = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return self.name


class StateChange(db.Model):

    __tablename__ = 'StateChange'

    id = db.Column(db.Integer, primary_key=True)

    created_at = db.Column(db.DateTime(timezone=True))
    modified_at = db.Column(db.DateTime(timezone=True))
    count = db.Column(db.Integer)
    path = db.Column(db.Text, nullable=True)

    state = db.relationship(
        "State", backref=db.backref('statechanges', order_by=id))
    pawprint = db.relationship(
        "Pawprint", backref=db.backref('statechanges', order_by=id))

    def repr(self):
        return "{} ({})".format(repr(self.pawprint), repr(self.state))


class Reference(db.Model):

    __tablename__ = 'Reference'

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.Text, nullable=True)
    ra = db.Column(db.Float, nullable=False)
    dec = db.Column(db.Float, nullable=False)
    FoV = db.Column(db.Float, nullable=False)

    def repr(self):
        return self.path


class Source(db.Model):

    __tablename__ = 'Source'

    id = db.Column(db.Integer, primary_key=True)
    ra = db.Column(db.Float, nullable=False)
    dec = db.Column(db.Float, nullable=False)
    mag = db.Column(db.Float, nullable=False)
    mag_err = db.Column(db.Float, nullable=False)
    class_source = db.Column(db.String, nullable=True)

    pawprint = db.relationship(
        "Pawprint", backref=db.backref('sources', order_by=id))

    def repr(self):
        return "({}, {})".format(self.ra, self.dec)


class Candidate(db.Model):

    __tablename__ = 'Candidate'

    PREDICTED_TYPES = [
        ("real", "Real"), ("bogus", "Bogus")
    ]

    id = db.Column(db.Integer, primary_key=True)
    ra = db.Column(db.Float, nullable=False)
    dec = db.Column(db.Float, nullable=False)
    mag = db.Column(db.Float, nullable=False)
    mag_err = db.Column(db.Float, nullable=False)
    predicted = db.Column(db.ChoiceType(PREDICTED_TYPES), nullable=True)

    pawprint = db.relationship(
        "Pawprint", backref=db.backref('candidates', order_by=id))
    stack = db.relationship(
        "Stack", backref=db.backref('candidates', order_by=id))

    def repr(self):
        return "({}, {})".format(self.ra, self.dec)


class StackState(db.Model):

    __tablename__ = 'StackState'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    folder = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, nullable=False)
    is_error = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return self.name


class StackStateChange(db.Model):

    __tablename__ = 'StackStateChange'

    id = db.Column(db.Integer, primary_key=True)

    created_at = db.Column(db.DateTime(timezone=True))
    modified_at = db.Column(db.DateTime(timezone=True))
    count = db.Column(db.Integer)
    path = db.Column(db.Text, nullable=True)

    stackstate = db.relationship(
        "StackState", backref=db.backref('stack_statechanges', order_by=id))
    stack = db.relationship(
        "Stack", backref=db.backref('stack_statechanges', order_by=id))

    def repr(self):
        return "{} ({})".format(repr(self.stack), repr(self.stackstate))


class Pawprint(db.Model):

    __tablename__ = 'Pawprint'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True))
    observation_date = db.Column(db.DateTime(timezone=True))
    modified_at = db.Column(db.DateTime(timezone=True))

    # agregar todo lo que el fits header tenga
    # y columnas adicionales

    state = db.relationship(
        "State", backref=db.backref('pawprints', order_by=id))
    campaign = db.relationship(
        "Campaign", backref=db.backref('pawprints', order_by=id))

    def repr(self):
        return self.id
