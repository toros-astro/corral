#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This module contains the table model definitions for toritos database.
# It uses the sqlalchemy orm to define the column structures


from corral import db


class Observatory(db.Model):
    """Model for observatories. SQLAlchemy Model object.
    """

    __tablename__ = 'Observatory'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return self.name


class CCD(db.Model):

    __tablename__ = 'CCD'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    brand = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    xpixsize = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return self.name


class Campaign(db.Model):

    __tablename__ = 'Campaign'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)

    observatory_id = db.Column(db.Integer, db.ForeignKey('Observatory.id'))
    observatory = db.relationship(
        "Observatory", backref=db.backref('campaigns', order_by=id))
    ccd_id = db.Column(db.Integer, db.ForeignKey('CCD.id'))
    ccd = db.relationship(
        "CCD", backref=db.backref('campaigns', order_by=id))

    def __repr__(self):
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

    state_id = db.Column(db.Integer, db.ForeignKey('State.id'))
    state = db.relationship(
        "State", backref=db.backref('statechanges', order_by=id))
    pawprint_id = db.Column(db.Integer, db.ForeignKey('Pawprint.id'))
    pawprint = db.relationship(
        "Pawprint", backref=db.backref('statechanges', order_by=id))

    def __repr__(self):
        return "{} ({})".format(repr(self.pawprint), repr(self.state))


class Reference(db.Model):

    __tablename__ = 'Reference'

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.Text, nullable=True)
    ra = db.Column(db.Float, nullable=False)
    dec = db.Column(db.Float, nullable=False)
    FoV = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return self.path


class Source(db.Model):

    __tablename__ = 'Source'

    id = db.Column(db.Integer, primary_key=True)
    ra = db.Column(db.Float, nullable=False)
    dec = db.Column(db.Float, nullable=False)
    mag = db.Column(db.Float, nullable=False)
    mag_err = db.Column(db.Float, nullable=False)
    class_source = db.Column(db.String, nullable=True)

    pawprint_id = db.Column(db.Integer, db.ForeignKey('Pawprint.id'))
    pawprint = db.relationship(
        "Pawprint", backref=db.backref('sources', order_by=id))

    def __repr__(self):
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

    pawprint_id = db.Column(db.Integer, db.ForeignKey('Pawprint.id'))
    pawprint = db.relationship(
        "Pawprint", backref=db.backref('candidates', order_by=id))
    stack_id = db.Column(db.Integer, db.ForeignKey('Stack.id'))
    stack = db.relationship(
        "Stack", backref=db.backref('candidates', order_by=id))

    def __repr__(self):
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

    stackstate_id = db.Column(db.Integer, db.ForeignKey('StackState.id'))
    stackstate = db.relationship(
        "StackState", backref=db.backref('stack_statechanges', order_by=id))
    stack_id = db.Column(db.Integer, db.ForeignKey('Stack.id'))
    stack = db.relationship(
        "Stack", backref=db.backref('stack_statechanges', order_by=id))

    def __repr__(self):
        return "{} ({})".format(repr(self.stack), repr(self.stackstate))


class Pawprint(db.Model):

    __tablename__ = 'Pawprint'

    id = db.Column(db.Integer, primary_key=True)
    jd = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True))
    observation_date = db.Column(db.DateTime(timezone=True))
    modified_at = db.Column(db.DateTime(timezone=True))
    simple = db.Column(db.String(8), nullable=True)
    bitpix = db.Column(db.Integer, nullable=True)
    naxis = db.Column(db.Integer, nullable=True)
    naxis1 = db.Column(db.Integer, nullable=True)
    naxis2 = db.Column(db.Integer, nullable=True)
    bscale = db.Column(db.Float, nullable=True)
    bzero = db.Column(db.Float, nullable=True)
    exposure = db.Column(db.Float, nullable=True)
    set_temp = db.Column(db.Float, nullable=True)
    xpixsz = db.Column(db.Float, nullable=True)
    ypixsz = db.Column(db.Float, nullable=True)
    exptime = db.Column(db.Integer, nullable=False)
    ccdtemp = db.Column(db.Float, nullable=True)
    imagetype = db.Column(db.String(32), nullable=False)
    targname = db.Column(db.String(40), nullable=True)
    xbinning = db.Column(db.Integer, nullable=False)
    ybinning = db.Column(db.Integer, nullable=False)
    readoutm = db.Column(db.String(24), nullable=True)
    imagetyp = db.Column(db.String(24), nullable=False)
    object_ = db.Column(db.String(24), nullable=True)
    observer = db.Column(db.String(48), nullable=True)

    state_id = db.Column(db.Integer, db.ForeignKey('State.id'))
    state = db.relationship(
        "State", backref=db.backref('pawprints', order_by=id))
    campaign_id = db.Column(db.Integer, db.ForeignKey('Campaign.id'))
    campaign = db.relationship(
        "Campaign", backref=db.backref('pawprints', order_by=id))

    def __repr__(self):
        return self.id


class Stack(db.Model):

    __tablename__ = 'Stack'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True))
    modified_at = db.Column(db.DateTime(timezone=True))
    path = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return self.id


class MasterCal(db.Model):

    __tablename__ = 'MasterCal'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True))
    modified_at = db.Column(db.DateTime(timezone=True))
    path = db.Column(db.Text, nullable=True)
    imagetype = db.Column(db.String(40), nullable=False)

    def __repr__(self):
        return self.id


class Combination(db.Model):

    __tablename__ = 'Combination'

    id = db.Column(db.Integer, primary_key=True)

    calfile_id = db.Column(db.Integer, db.ForeignKey('CalFile.id'))
    calfile = db.relationship(
        "CalFile", backref=db.backref('combinations', order_by=id))
    mastercal_id = db.Column(db.Integer, db.ForeignKey('MasterCal.id'))
    mastercal = db.relationship(
        "MasterCal", backref=db.backref('combinations', order_by=id))

    def __repr__(self):
        return self.id


class CalFile(db.Model):

    __tablename__ = 'CalFile'

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.Text, nullable=True)
    observation_date = db.Column(db.DateTime(timezone=True))
    exptime = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True))
    imagetype = db.Column(db.String(16), nullable=False)

    def __repr__(self):
        return self.id
