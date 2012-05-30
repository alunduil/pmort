# -*- coding: utf-8 -*-

# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
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

import sys
import os
import re
import logging

from pmort.plugins import PostMortemPlugin
from pmort.parameters.configuration import PostMortemConfiguration

class ShellRunner(PostMortemPlugin):
    def log(self, output = sys.stdout):
        for script, interpreter in ShellScripts():
            logging.info("Running Shell Script:  %s %s", interpreter, script)
            if output == sys.stdout:
                output.write(subprocess.check_output([interpreter, script]))
            else:
                logging.debug("Logging into %s", os.path.join(os.path.abspath(os.path.dirname(output.name)), script.split("/")[-1] + ".log"))
                with open(os.path.join(os.path.abspath(os.path.dirname(output.name)), script.split("/")[-1] + ".log"), "w") as output:
                    output.write(subprocess.check_output([interpreter, script]))

class ShellScripts(object):
    def __init__(self, shell_directory = None):
        self._commands = {}

        directories = [
                os.path.join(os.path.abspath(os.path.dirname(__file__)), "shell_scripts"),
                os.path.join(re.sub(r"usr/", "usr/local/", os.path.abspath(os.path.dirname(__file__))), "shell_scripts"),
                "/etc/pmort/shell_scripts",
                os.path.expanduser(os.path.join("~", ".config", "pmort", "shell_scripts")),
                shell_directory,
                ]

        for directory in directories:
            logging.debug("Checking for shell scripts in %s", directory)

            if not directory or not os.access(directory, os.R_OK):
                continue

            for file_name in os.listdir(directory):
                logging.debug("Checking if %s is a shell script", os.path.join(directory, file_name))

                with open(file_name, "r") as file_:
                    shebang = file_.readline()
                    if shebang.startswith("!#"):
                        logging.debug("Found shell script, %s, using interpreter %s", os.path.join(directory, file_name), shebang.strip()[2:])
                        self._commands[os.path.join(directory, file_name)] = shebang.strip()[2:]

    def __len__(self):
        return len(self._commands)

    def __getitem__(self, key):
        return self._commands[key]

    def __setitem__(self, key, value):
        self._commands[key] = value

    def __delitem__(self, key):
        del self._commands[key]

    def __iter__(self):
        for command, interpreter in self._commands.iteritems():
            yield command, interpreter

    def __contains__(self, item):
        return item in self._commands

if __name__ == "__main__":
    ShellRunner().log()

