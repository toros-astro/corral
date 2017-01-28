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

import abc
import datetime
import smtplib
import codecs
from email.mime.text import MIMEText

import six

from .. import util

conf = util.dimport("corral.conf", lazy=True)


# =============================================================================
# BASE CLASS
# =============================================================================

@six.add_metaclass(abc.ABCMeta)
class EndPoint(object):

    def setup(self, alert):
        self._alert = alert

    @abc.abstractmethod
    def process(self):
        raise NotImplementedError()  # pragma: no cover

    def teardown(self, type, value, traceback):
        self._alert = None
        pass

    def render_alert(self, obj):
        now = datetime.datetime.utcnow()
        return self._alert.render_alert(now, self, obj)

    @property
    def alert(self):
        return self._alert


# =============================================================================
# EMAIL
# =============================================================================

class Email(EndPoint):

    def __init__(self, to, sent_from=None, subject=None, message=None):
        self.server = None
        self.to = to
        self.sent_from = sent_from
        self.subject = subject
        self.message = message

    def setup(self, alert):
        super(Email, self).setup(alert)
        self.server = smtplib.SMTP(conf.settings.EMAIL["server"])
        if conf.settings.EMAIL["tls"]:
            self.server.ehlo()
            self.server.starttls()
        self.server.login(
            conf.settings.EMAIL["user"], conf.settings.EMAIL["password"])

    def teardown(self, *args):
        super(Email, self).teardown(*args)
        self.server.quit()

    def get_recipients(self, obj):
        return self.to

    def get_sent_from(self, obj):
        if self.sent_from is not None:
            return self.sent_from
        user = conf.settings.EMAIL["user"]
        if "@" in user:
            return conf.settings.EMAIL["user"]
        return "{}@{}".format(
            conf.settings.EMAIL["user"],
            conf.settings.EMAIL["server"].split(":", 1)[0])

    def get_subject(self, obj):
        if self.subject is not None:
            return self.subject
        return "[ALERT - {}] {}".format(
            conf.PACKAGE, type(self.alert).__name__)

    def get_message(self, obj):
        if self.message is not None:
            return self.message.format(obj)
        return self.render_alert(obj)

    def process(self, obj):
        to = self.get_recipients(obj)
        sent_from = self.get_sent_from(obj)
        message = self.get_message(obj)

        msg = MIMEText(message)
        msg['Subject'] = self.get_subject(obj)
        msg['From'] = sent_from
        msg['To'] = ",".join(to)

        self.server.sendmail(sent_from, to, msg.as_string())


class File(EndPoint):

    MEMORY = ":memory:"

    def __init__(self, path, mode="a", encoding="utf8"):
        self.path = path
        self.mode = mode
        self.encoding = encoding

    def setup(self, alert):
        super(File, self).setup(alert)
        if self.path == File.MEMORY:
            self.fp = six.StringIO()
        else:
            self.fp = codecs.open(self.path, self.mode, self.encoding)

    def teardown(self, *args):
        super(File, self).teardown(*args)
        if self.path != File.MEMORY and self.fp and not self.fp.closed:
            self.fp.close()

    def process(self, obj):
        self.fp.write(self.render_alert(obj))
