#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs as _codecs
import argparse as _argparse
import sys as _sys
from gettext import gettext as _


import six as _six


if _six.PY2:

    class FileType(object):
        """Factory for creating file object types with unicode patch

        Instances of FileType are typically passed as type= arguments to the
        ArgumentParser add_argument() method.

        Keyword Arguments:
            - mode -- A string indicating how the file is to be opened.
              Accepts the same values as the builtin open() function.
            - bufsize -- The file's desired buffer size. Accepts the same
              values as the builtin codecs.open() function.
            - encoding -- default utf8
        """

        def __init__(self, mode='r', bufsize=-1, encoding="utf8"):
            self._mode = mode
            self._bufsize = bufsize
            self._encoding = "utf8"

        def __call__(self, string):
            # the special argument "-" means sys.std{in,out}
            if string == '-':
                if 'r' in self._mode:
                    return _sys.stdin
                elif 'w' in self._mode:
                    return _sys.stdout
                else:
                    msg = _('argument "-" with mode %r') % self._mode
                    raise ValueError(msg)

            # all other arguments are used as file names
            try:
                return _codecs.open(string, mode=self._mode,
                                    encoding=self._encoding,
                                    buffering=self._bufsize)
            except IOError as e:
                message = _("can't open '%s': %s")
                raise _argparse.ArgumentTypeError(message % (string, e))

        def __repr__(self):
            args = self._mode, self._bufsize, self._encoding
            args_str = ', '.join(repr(arg) for arg in args if arg != -1)
            return '%s(%s)' % (type(self).__name__, args_str)

else:

    FileType = _argparse.FileType
