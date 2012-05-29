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

PostMortemParameters = [
        {
            # --daemonize, -d
            "option_strings": ["--daemonize", "-d"],
            "action": "store_true",
            "default": False,
            "help": "".join([
                "Specifies that the application should run as a ",
                "daemon and persist in running forever.  This option ",
                "ensures that proper deamonization occurs ",
                "automatically rather than relying on something ",
                "external such as cron or start-stop-daemon.",
                ]),
            },
        {   
            # --pidfile, -p
            "option_strings": ["--pidfile", "-P"],
            "default": "/var/run/pmort.pid",
            "help": "".join([
                "Specifies the location of the process tracking ",
                "file.  Defaults to /var/run/pmort.pid.",
                ]),
            },
        {
            # --configuration, -f
            "option_strings": ["--configuration", "-f"],
            "default": "/etc/pmort/pmort.conf",
            "help": "".join([
                "Specifies the location of the configuration file ",
                "used to change the daemon's behaviour.",
                ]),
            },
        {
            # --cache, -c
            "option_strings": ["--cache", "-c"],
            "default": "/var/cache/pmort",
            "help": "".join([
                "Specifies the directory that all cache files for ",
                "pmort are saved to.  Defaults to /var/cache/pmort.",
                ]),
            },
        {
            # --log_directory, -L
            "option_strings": ["--log_directory", "-L"],
            "default": "/var/log/pmort",
            "help": "".join([
                "Specifies the directory to log plugin output.  If ",
                "'-' is specified all output will be sent to stdout.",
                ]),
            },
        {
            # --log_level, -l
            "option_strings": ["--log_level", "-l"],
            "choices": ["debug", "info", "warning", "error", "critical"],
            "default": "warning",
            "help": "".join([
                "Specifies the logging level (verbosity of the daemons ",
                "logging output).",
                ]),
            },
        {
            # --polling_interval, -p
            "option_strings": ["--polling_interval", "-p"],
            "type": int,
            "metavar": "POLL",
            "help": "".join([
                "Specifies the number of seconds to wait between ",
                "iterations.  The number specified is used as a ",
                "guideline for the polling interval in conjunction ",
                "with the learned threshold load in the following ",
                "way: REAL_POLL = (1 - LOAD_CUR/LOAD_THRESH)*POLL + ",
                "LOAD_CUR/LOAD_THRESH.  LOAD_THRESH is learned to be ",
                "the highest load this application encounters on the ",
                "system.",
                ]),
            },
        {
            # --username, -u
            "option_strings": ["--username", "-u"],
            "default": "pmort",
            "help": "".join([
                "Specifies the user for the daemon to run as.  ",
                "Defaults to pmort.  If this user doesn't exist on ",
                "the system another username will need to be ",
                "specified.",
                ]),
            },
        {
            # --group, -g
            "option_strings": ["--group", "-g"],
            "default": "pmort",
            "help": "".join([
                "Specifies the group for the daemon to run as.  ",
                "Defaults to pmort.  If this user doesn't exist on ",
                "the system another username will need to be ",
                "specified.",
                ]),
            },
        ]

