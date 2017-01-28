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

import sys
import copy
import argparse
import os
from collections import defaultdict

from termcolor import colored

import six

from .. import core, util, exceptions
from .base import BaseCommand, MODE_IN, MODE_OUT, MODE_TEST, MODE_NOPIPE

conf = util.dimport("corral.conf", lazy=True)


# =============================================================================
# CLASS
# =============================================================================

class CorralArgumentParserError(Exception):
    pass


class CorralHelpFormatter(argparse.HelpFormatter):
    pass


class CorralArgumentParser(argparse.ArgumentParser):

    def error(self, message):
        raise CorralArgumentParserError(message)


class CorralCLIParser(object):

    def __init__(self, description):
        usage = ("run 'python {} <COMMAND> --help'").format(sys.argv[0])

        self.global_parser = CorralArgumentParser(
            description=description, usage=usage,
            formatter_class=CorralHelpFormatter)
        self.global_parser.add_argument(
            "--version", "-v", action="version", version=core.get_version())
        self.global_parser.add_argument(
            "-x", "--stacktrace", dest="stacktrace",
            action="store_true", default=False)

        self.subparsers = self.global_parser.add_subparsers()
        self.help_texts = defaultdict(list)

    def _defaut_scmd_fmt(self, scmd, htext, max_line_length, color):
        line = "  {} - {}".format(color(scmd, "green"), htext)
        if max_line_length and len(line) > max_line_length:
            line = line[:max_line_length-3] + "..."
        return line

    def main_help_text(self, max_line_length=80, color=True):
        color = colored if color else (lambda t: t)
        scmd_fmt = self._defaut_scmd_fmt
        usage = ["", self.global_parser.usage, "", "Available subcommands", ""]
        usage.extend([color("[corral]", "red")])
        usage.extend(
                scmd_fmt(hparts[0], hparts[1], max_line_length, color)
                for hparts in sorted(self.help_texts["corral"]))

        pkgs = [k for k in self.help_texts.keys() if k != "corral"]
        for pkg in pkgs:
            pkg_title = "[{}]".format(pkg)
            usage.extend(["", color(pkg_title, "red")])
            usage.extend(
                scmd_fmt(hparts[0], hparts[1], max_line_length, color)
                for hparts in sorted(self.help_texts[pkg]))

        return "\n".join(usage)

    def add_subparser(self, title, command, mode, **kwargs):
        if mode not in (MODE_IN, MODE_OUT, MODE_TEST, MODE_NOPIPE):
            msg = "Command mode must be '{}', '{}', or '{}'. Found '{}'"
            raise ValueError(MODE_IN, MODE_OUT, MODE_TEST, msg.format(mode))
        parser = self.subparsers.add_parser(title, **kwargs)
        parser.set_defaults(command=command)
        parser.set_defaults(mode=mode)

        project = command.__module__.split(".", 1)[0]
        description = " ".join(
            p.strip() for p in parser.description.split() if p.strip())
        help_parts = (title, description or "-")
        self.help_texts[project].append(help_parts)
        return parser

    def extract_func(self, ns):
        kwargs = dict(ns._get_kwargs())
        command = kwargs.pop("command")
        mode = kwargs.pop("mode")
        func_kwargs, global_kwargs = {}, {}
        for k, v in kwargs.items():
            if k in ("stacktrace",):
                global_kwargs[k] = v
            else:
                func_kwargs[k] = v
        return command, mode, func_kwargs, global_kwargs

    def parse_args(self, argv):
        parsed_args = self.global_parser.parse_args(argv)
        return self.extract_func(parsed_args)


# =============================================================================
# FUNCTIONS
# =============================================================================

def load_commands_module():
    if conf.settings.has_module("commands"):
        try:
            commands_module = "{}.commands".format(conf.PACKAGE)
            return util.dimport(commands_module)
        except ImportError as err:
            core.logger.error("On load commands: " + six.text_type(err))


def load_project_commands():
    commands_module = load_commands_module().__name__
    commands = [
        cmd for cmd in util.collect_subclasses(BaseCommand)
        if cmd.__module__ == commands_module]
    return commands


def create_parser():

    from . import commands  # noqa

    in_pipeline = "CORRAL_SETTINGS_MODULE" in os.environ

    try:
        load_commands_module()
    except:
        if in_pipeline:
            raise

    command_names = set()

    description = core.get_description()
    parser = CorralCLIParser(description)

    for cls in util.collect_subclasses(BaseCommand):

        options = copy.deepcopy(cls.get_options())

        title = options.pop("title")
        mode = options.pop("mode")

        if mode != MODE_NOPIPE and in_pipeline is False:
            continue

        if title in command_names:
            msg = "Duplicate Command '{}'".format(title)
            raise exceptions.ImproperlyConfigured(msg)
        command_names.add(title)

        command = cls()
        sub_parser = parser.add_subparser(title, command, mode, **options)
        command.configure(sub_parser)
        command.setup()

    return parser


def run_from_command_line():
    parser = create_parser()
    if sys.argv[1:] in (['--help'], ['-h']):
        sys.stdout.write(parser.main_help_text() + "\n\n")
        sys.exit(0)
    try:
        command, mode, kwargs, gkwargs = parser.parse_args(sys.argv[1:])
    except CorralArgumentParserError as err:
        sys.stdout.write(parser.main_help_text() + "\n\n")
        sys.stderr.write("Error: " + str(err) + "\n\n")
        sys.exit(1)
    else:
        if mode == MODE_IN:
            core.setup_environment()
        elif mode == MODE_TEST:
            core.setup_environment(test_mode=True)
        try:
            command.handle(**kwargs)
        except BaseException as err:
            sys.stderr.write("{}\n".format(err))
            if gkwargs.get("stacktrace"):
                six.reraise(type(err), err, six.sys.exc_traceback)
        if command.exit_status:
            sys.exit(command.exit_status)
