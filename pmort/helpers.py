# -*- coding: utf-8 -*-

# Copyright (C) 2011 by Alex Brandt <alunduil@alunduil.com>
#
# This program is free software; you can redistribute it and#or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place - Suite 330, Boston, MA  02111-1307, USA.

"""Helper functions.

Simple things like printing common errors, verbose, and debugging output.

"""

__all__ = [
        "error",
        "debug",
        "verbose",
        ]

import sys
import os
import itertools
import re
import inspect

from inspect import stack

from pmort.colors import TerminalController

TERMINAL = TerminalController()

COLORIZE = "none"

def colorize(color, message, out = sys.stdout):
    """Colorize the given message with the given color.

    If COLOR is "none" we shall simply bypass colorizing otherwise we will try
    to add the requested appropriate color.

    """
    if COLORIZE == "none":
        print >> out, message
    else:
        print >> out, TERMINAL.render('${{{color}}}{message}${{NORMAL}}'.format(
            color = color, message = message))

def debug(message = None, *args, **kwargs):
    """Print a debugging message to the standard error."""

    output = []

    if message and len(args):
        output.append(message.format(args))
    elif message:
        output.append(message)

    if len(kwargs.values()):
        output.extend([ 
            "{key} -> {value}".format(
                key = key,
                value = val
                ) for key, val in kwargs.items()
            ])

    def stack_item(level):
        """Return details about the level of the current stack."""
        return "{file_}:{line} in {function}".format(file_ = stack()[level][1],
                line = stack()[level][2], function = stack()[level][3])

    for line in output:
        colorize("YELLOW", "D: {called} called from {caller}: {line}".format(
            called = stack_item(2), caller = stack_item(3), line = line),
            sys.stderr)

def verbose(message = None, *args, **kwargs):
    """Print a verbose message to the standard error."""

    output = []

    if message and len(args):
        output.append(message.format(*args))
    elif message:
        output.append(message)

    if len(kwargs.values()):
        output.extend([
            "{key} -> {value}".format(
                key = key,
                value = val
                ) for key, val in kwargs.items()
            ])

    for line in output:
        colorize("BLUE", "V: {line}".format(line = line), sys.stderr)

def error(message = None, *args, **kwargs):
    """Print an error message to the standard error."""

    output = []

    if message and len(args):
        output.append(message.format(args))
    elif message:
        output.append(message)

    if len(kwargs.values()):
        output.extend([
            "{key} -> {value}".format(
                key = key,
                value = val
                ) for key, val in kwargs.items()
            ])

    for line in output:
        colorize("RED", "E: {line}".format(line = line), sys.stderr)

def issubclass(class_a, class_b):
    """Determine if class A is a subclass of class_b."""
    return class_b in [
            clsobj.__name__ for clsobj in inspect.getmro(class_a)
            ]

