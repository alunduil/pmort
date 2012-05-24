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

import argparse
import datetime
import sys

import pmort.helpers as helpers

class PostMortemApplication(object): #pylint: disable-msg=R0903
    def __init__(self):
        self._debug = False
        self._verbose = False
        self._quiet = False

        self.arguments = PostMortemOptions(sys.argv[0]).parsed_args

        # If we have debugging turned on we should also have verbose.
        if self.arguments.debug: 
            self.arguments.verbose = True

        # If we have verbose we shouldn't be quiet.
        if self.arguments.verbose: 
            self.arguments.quiet = False

        # Other option handling ...
        helpers.COLORIZE = self.arguments.color

    def run(self):
        verbosity = {
                "verbose": self.arguments.verbose,
                "debug": self.arguments.debug,
                }

        account = Account.login(
                username = self.arguments.username,
                password = self.arguments.password,
                provider = self.arguments.cloud
                )

        previous = Storage(**verbosity)

        if self.arguments.debug:
            helpers.debug({
                "servers":account.servers,
                })

        add = list(set(account.servers) - set(previous.servers))
        remove = list(set(previous.servers) - set(account.servers))

        if self.arguments.debug:
            helpers.debug({
                "add":add,
                "remove":remove,
                })

        verbosity["plugin_directory"] = self.arguments.plugins

        for plugin in PostMortemPlugins(**verbosity):
            for server in add:
                plugin.add(server)
            for server in remove:
                plugin.remove(server)

        previous.servers = account.servers

class PostMortemOptions(object):
    def __init__(self, name):
        self._parser = argparse.ArgumentParser(prog = name)
        self._parser = self._add_args()

    @property
    def parser(self):
        return self._parser

    @property
    def parsed_args(self):
        return self._parser.parse_args()

    def _add_args(self):
        """Add the options to the parser."""

        self._parser.add_argument("--version", action = "version", 
                version = "%(prog)s 9999")

        # --verbose, -v
        help_list = [
                "Specifies verbose output.",
                ]
        self._parser.add_argument("--verbose", "-v", action = "store_true",
                default = "", help = "".join(help_list))

        # --debug, -D
        help_list = [
                "Specifies debugging output.  Implies verbose output.",
                ]
        self._parser.add_argument("--debug", "-D", action = "store_true",
                default = False, help = "".join(help_list))

        # --quiet, -q
        help_list = [
                "Specifies quiet output.  This is superceded by verbose ",
                "output.",
                ]
        self._parser.add_argument("--quiet", "-q", action = "store_true",
                default = False, help = "".join(help_list))
        
        # --color=[none,light,dark,auto]
        help_list = [
                "Specifies whether output should use color and which type of ",
                "background to color for (light or dark).  This defaults to ",
                "auto.",
                ]
        self.parser.add_argument("--color", 
                choices = ["none", "light", "dark", "auto"], default = "auto",
                help = "".join(help_list))

        return self._parser

