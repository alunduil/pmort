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
import sys
import daemon
import lockfile
import signal
import pwd
import grp
import os
import threading
import logging

import pmort.helpers as helpers

from datetime import datetime

from pmort.plugins import PostMortemPlugins
from pmort.parameters import PostMortemParameters

class PostMortemApplication(object): #pylint: disable-msg=R0903
    def __init__(self):
        self.arguments = PostMortemOptions(sys.argv[0]).parsed_args

        # Other option handling ...
        if not self.arguments.log_directory.startswith("-"):
            logging.basicConfig(filename = os.path.join(self.arguments.log_directory, "pmort.log"), level = getattr(logging, self.arguments.log_level.upper()))
        else:
            logging.basicConfig(level = getattr(logging, self.arguments.log_level.upper()))

        logging.debug("self.arguments.daemonize:%s", self.arguments.daemonize)

        if self.arguments.daemonize:
            self.run = self.daemonize
        else:
            self.run = self.iteration

    @property
    def load_threshold(self):
        ret = 0.1

        if os.access(os.path.join(self.arguments.cache, "load_threshold"), os.R_OK):
            threshold = open(os.path.join(self.arguments.cache, "load_threshold"), "r")
            ret = threshold.readlines()
            threshold.close()

        logging.debug("load_threshold:%s", ret)

        return ret

    def learn(self):
        if os.getloadavg()[0] > self.load_threshold:
            file_ = open(os.path.join(self.arguments.cache, "load_threshold"), "w")
            file_.write(unicode(os.getloadavg()[0]))
            file_.close()

    def iteration(self):
        if os.getloadavg()[0] > self.load_threshold:
            self.parallel_iteration()
        else:
            self.serial_iteration()
        self.learn()

    def serial_iteration(self):
        for plugin in PostMortemPlugins():
            self._single_iteration(plugin)

    def _single_iteration(self, plugin):
        if self.arguments.log_directory.startswith("-"):
            output = sys.stdout
            output.write(repr(plugin) + ":")
        else:
            now = datetime.now()
            log_path = os.path.join(self.arguments.log_directory, now.strftime("%Y%m%d%H%M%S"))
            if not os.access(log_path, os.W_OK):
                os.mkdir(log_path)
            output = open(os.path.join(log_path, repr(plugin) + ".log"), "w")

        plugin.log(output = output)
        output.flush()
        output.close()

    def parallel_iteration(self):
        for plugin in PostMortemPlugins():
            thread = threading.Thread(target = self._single_iteration, name = plugin, args = (self, plugin))
            thread.start()

        if self.arguments.debug:
            helpers.debug({
                "threading.active_count()":threading.active_count(),
                "threading.enumerate()":threading.enumerate(),
                })

    def daemonize(self):

        context = daemon.DaemonContext(
                working_directory = '/',
                umask = 0o002,
                pidfile = lockfile.FileLock(self.arguments.pidfile),
                )

        context.files_preserve = [
                logging.getLogger().__dict__["handlers"][0].__dict__["stream"],
                ]

        def stop():
            pass

        def reinitialize():
            pass

        def iteration():
            return self.iteration()

        context.signal_map = {
                signal.SIGTERM: stop,
                signal.SIGHUP: reinitialize,
                signal.SIGINT: 'terminate',
                signal.SIGALRM: iteration,
                }

        logging.info("Starting the daemon ...")
        with context:
            logging.info("Scheduling the first run.")
            self.schedule()
            logging.info("Pausing this process to let the handlers take over.")
            signal.pause()

    def schedule(self):
        load_ratio = os.getloadavg()[0]/self.load_threshold
        sleep_time = (1.0 - load_ratio)*self.arguments.poll_seconds + load_ratio
        signal.alarm(sleep_time)

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

        for parameter in PostMortemParameters:
            option_strings = parameter["option_strings"]
            del parameter["option_strings"]
            self.parser.add_argument(*option_strings, **parameter)
            parameter["option_strings"] = option_strings

        return self._parser

