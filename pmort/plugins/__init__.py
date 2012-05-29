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

import os
import re
import sys
import itertools
import inspect

from pmort import helpers

from pmort.helpers import issubclass

class PostMortemPlugin(object):
    def log(self, output = sys.stdout):
        """Logs the data for the plugin to the output file."""
        raise NotImplementedError

    def __repr__(self):
        return unicode(self)

    def __unicode__(self):
        return unicode(self.__class__).rsplit('.')[-1][:-2]

class PostMortemPlugins(object):
    def __init__(self, plugin_directory = None, verbose = False, debug = False):
        self._verbose = verbose
        self._debug = debug

        self._commands = {}

        directories = [
                os.path.join(os.path.abspath(os.path.dirname(__file__))),
                os.path.join(re.sub(r"usr/", "usr/local/", os.path.abspath(os.path.dirname(__file__)))),
                os.path.expanduser(os.path.join("~", ".config", "pmort", "plugins.d")),
                plugin_directory,
                ]

        for directory in directories:
            if self._debug:
                helpers.debug({
                    "directory":directory,
                    })

            if not directory or not os.access(directory, os.R_OK):
                continue

            sys.path.append(directory)

            if self._debug:
                helpers.debug({
                    "os.listdir(directory)":os.listdir(directory),
                    })

            module_names = list(set([ re.sub(r"\.py.?", "", file_name) for file_name in os.listdir(directory) if not file_name.startswith("_") ]))

            if self._debug:
                helpers.debug({
                    "module_names":module_names,
                    })

            modules = [ __import__(module_name, globals(), locals(), [], -1) for module_name in module_names ]

            for module in modules:
                for object_ in [ object_() for name, object_ in inspect.getmembers(module, inspect.isclass) if issubclass(object_, "PostMortemPlugin") ]:
                    self._commands[repr(object_)] = object_

        del self._commands["PostMortemPlugin"]

        if self._debug:
            helpers.debug({
                "self._commands":self._commands,
                "self._commands.values()":self._commands.values(),
                })

        self._commands = self._commands.values()

    def __len__(self):
        return len(self._commands)

    def __getitem__(self, key):
        return self._commands[key]

    def __setitem__(self, key, value):
        self._commands[key] = value

    def __delitem__(self, key):
        del self._commands[key]

    def __iter__(self):
        for command in self._commands:

            if self._debug:
                helpers.debug({
                    "command":command,
                    })

            yield command

    def __reversed__(self):
        tmp = self._commands
        tmp.reverse()
        return tmp

    def __contains__(self, item):
        return item in self._commands

