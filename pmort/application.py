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
from pmort.parameters import PostMortemArguments
from pmort.learning import Learner

class PostMortemApplication(object):
    def __init__(self):
        self.arguments = PostMortemArguments("pmort")

        if self.arguments.log_directory.startswith("-"):
            logging.basicConfig(
                    level = getattr(logging, self.arguments.log_level.upper())
                    )
        else:
            logging.basicConfig(
                    filename = os.path.join(self.arguments.log_directory, "pmort.log"), 
                    level = getattr(logging, self.arguments.log_level.upper())
                    )

        self.learner = Learner(self.arguments.cache)

        if self.arguments.daemonize:
            self.run = self.daemonize
        else:
            self.run = self.iteration

    def iteration(self):
        if os.getloadavg()[0] > self.load_threshold:
            logging.info("Running a parallel iteration.")
            self.parallel_iteration()
        else:
            logging.info("Running a serial iteration.")
            self.serial_iteration()

        self.learn()
        self.schedule()

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

        logging.info("Running plugin {0}".format(repr(plugin)))

        plugin.log(output = output)

        output.flush()
        if output != sys.stdout:
            output.close()

    def parallel_iteration(self):
        for plugin in PostMortemPlugins():
            thread = threading.Thread(target = self._single_iteration, name = plugin, args = (self, plugin))
            thread.start()

        logging.debug("Active Thread Count:%s", threading.active_count())
        logging.debug("Enumerated Threads:%s", threading.enumerate())

    def daemonize(self):

        if os.access(self.arguments.pidfile, os.R_OK):
            with open(self.arguments.pidfile, "r") as pidfile:
                pid = pidfile.readline()
                if os.path.exists("/proc/{0}".format(pid)):
                    logging.error("Found already running process with pid {0}".format(pid))
                    sys.exit(1)
                else:
                    logging.warning("Breaking the lock file.")
                    lockfile.LockFile(self.arguments.pidfile).break_lock()
                    logging.warning("Removing the stale pid file.")
                    os.remove(self.arguments.pidfile)

        context = daemon.DaemonContext(
                umask = 0o002,
                pidfile = lockfile.FileLock(self.arguments.pidfile),
                )

        # TODO Remove this.
        if self.arguments.log_level.lower() == "debug":
            context.working_directory = os.getcwd()

        context.files_preserve = []
        context.files_preserve.extend([ 
            file_.__dict__["stream"]  for file_ in logging.getLogger().__dict__["handlers"]
            ])

        def stop(signum, frame):
            logging.info("Stopping the daemon.")
            context.close()
            logging.info("Removing the pidfile.")
            os.remove(self.arguments.pidfile)
            sys.exit(0)

        def reinitialize(signum, frame):
            # TODO Do something here.
            pass

        def iteration(signum, frame):
            logging.info("Starting an iteration.")
            return self.iteration()

        context.signal_map = {
                signal.SIGTERM: stop,
                signal.SIGHUP: reinitialize,
                signal.SIGINT: 'terminate',
                signal.SIGALRM: iteration,
                }

        logging.info("Starting the daemon ...")
        with context:
            with open(self.arguments.pidfile, "w") as pidfile:
                logging.info("Writing the pidfile.")
                pidfile.write(unicode(os.getpid()))
            logging.info("Scheduling the first run.")
            self.schedule()

    def schedule(self):
        load_ratio = os.getloadavg()[0]/float(self.learner["load_threshold"])
        sleep_time = max((1.0 - load_ratio)*float(self.arguments.polling_interval) + load_ratio, 1.0)
        logging.info("Current Sleep Time: %s", int(sleep_time))
        signal.alarm(int(sleep_time))
        signal.pause()

