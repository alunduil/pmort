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

"""pmort application driver.

This module contains the driving class for pmort.  This class handles the 
daemonization and option parsing; connecting all of the components into an
easy to run unit.

"""

import sys
import daemon
import lockfile
import signal
import os
import threading
import logging
import re

from datetime import datetime

from pmort.plugins import PostMortemPlugins
from pmort.parameters import PostMortemArguments
from pmort.learning import Learner

class PostMortemApplication(object):
    """Application driver class.

    This class defines a few items that are publicly accessible but the
    simplest invocation is to instantiate (no parameters required) and then
    call the run method.  It is assumed that this class will be called by an
    application looking to relinquish control (more so in the daemon instance).

    Examples:

    app = PostMortemApplication()
    app.run()

    """

    def __init__(self):
        self.arguments = PostMortemArguments("pmort")

        if self.arguments.log_directory.startswith("-"):
            logging.basicConfig(
                    level = getattr(logging, self.arguments.log_level.upper())
                    )
        else:
            logging.basicConfig(
                    filename = os.path.join(
                        self.arguments.log_directory,
                        "pmort.log"), 
                    level = getattr(logging, self.arguments.log_level.upper())
                    )

        self.learner = Learner(self.arguments.cache)

        if self.arguments.daemonize:
            self.run = self.daemonize
        else:
            self.run = self.iteration

    def iteration(self):
        """A single iteration of pmort.

        This method runs a particular iteration of updates on the plugins and
        no more.  This method does choose whether to parallelize the iteration
        or run it in serial based on the current system load.

        Examples:

        app.iteration()

        """

        if os.getloadavg()[0] > self.learner["load_threshold"]:
            logging.info("Running a parallel iteration.")
            self.parallel_iteration()
        else:
            logging.info("Running a serial iteration.")
            self.serial_iteration()

        self.learner.learn()
        self.schedule()

    def serial_iteration(self):
        """A single serial iteration of pmort.

        Serially executes the plugins that are found.

        """

        for plugin in PostMortemPlugins():
            self._single_iteration(plugin)

    def _single_iteration(self, plugin):
        """Common code for a single iteration of pmort.

        The common piece of the serial and parallel iterations of pmort.
        Handles the determination of output files for the plugins and actually
        running the plugins.
        
        Will output the plugins to stdout if log_directory is '-'; otherwise, 
        the plugin will be directed to write to log_directory/plugin.log.

        """

        if self.arguments.log_directory.startswith("-"):
            output = sys.stdout
            output.write(repr(plugin) + ":")
        else:
            now = datetime.now()
            log_path = os.path.join(self.arguments.log_directory,
                    now.strftime("%Y%m%d%H%M%S"))
            if not os.access(log_path, os.W_OK):
                os.mkdir(log_path)
            output = open(os.path.join(log_path, repr(plugin) + ".log"), "w")

        logging.info("Running plugin {0}".format(repr(plugin)))

        plugin.log(output = output)

        output.flush()
        logging.debug("The output file: %s", output)
        if output != sys.stdout:
            logging.debug("Creating the current symlink")

            target = os.path.join(output.name.rsplit('/', 2)[0], "current")

            logging.debug("Target of the symlink: %s", target)
            logging.debug("Source name: %s", output.name)

            if os.access(target, os.W_OK):
                os.remove(target)
            os.symlink(output.name, target)
            output.close()

    def parallel_iteration(self):
        """A single parallel iteration of pmort.

        Executes the plugins in their own thread to let as many finish as
        possible even when the system is under duress.

        """

        for plugin in PostMortemPlugins():
            thread = threading.Thread(target = self._single_iteration,
                    name = plugin, args = (self, plugin))
            thread.start()

        logging.debug("Active Thread Count:%s", threading.active_count())
        logging.debug("Enumerated Threads:%s", threading.enumerate())

    @property
    def last_directory(self):
        directories = sorted([ int(file_name) for file_name in os.listdir(self.arguments.log_directory) if re.match(r"\d+", file_name) ])
        return directories[-1]

    def daemonize(self):
        """Start the pmort deamon process and schedule the first run.

        Utilizing the daemon library we initialize the context for the daemon
        to run in (leveraging configuration file and argument parameters).  
        This is fairly typical daemon launching code and a larger discussion on
        the subject can be found at: http://www.python.org/dev/peps/pep-3143/.

        """

        if os.access(self.arguments.pidfile, os.R_OK):
            with open(self.arguments.pidfile, "r") as pidfile:
                pid = pidfile.readline()
                if os.path.exists("/proc/{0}".format(pid)):
                    logging.error("Found already running process with pid %s",
                            pid)
                    sys.exit(1)
                else:
                    target = os.path.join(self.arguments.log_directory, "lastcrash")
                    if os.access(target, os.W_OK):
                        os.remove(target)
                    os.symlink(
                            os.path.join(self.arguments.log_directory, unicode(self.last_directory)),
                            target
                            )
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
            """Properly stop the daemon.

            When the appropriate signal is caught we want to shutdown the
            daemon nicely.  This simply means closing the daemon context,
            removing the pidfile and exiting successfully.

            """

            logging.info("Stopping the daemon.")
            context.close()

            logging.info("Removing the pidfile.")
            os.remove(self.arguments.pidfile)

            logging.info("Exiting.")
            sys.exit(0)

        def reinitialize(signum, frame):
            """Properly reinitialize the daemon.

            When the appropriate signal is caught we want to re-read the 
            configuration file and let the updated parameters to take effect 
            (i.e. polling_interval, etc).  For items like changes to log
            locations a restart of the daemon is required.

            """

            # TODO Do something here.
            pass

        def iteration(signum, frame):
            """Run an iteration of pmort.

            When the appropraite signal, ALRM, is caught we want to actually
            run pmort and record the information it's configured to record.

            """

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
            target = os.path.join(self.arguments.log_directory, "lastshutdown")
            if os.access(target, os.W_OK):
                os.remove(target)
            os.symlink(
                    os.path.join(self.arguments.log_directory, unicode(self.last_directory)),
                    target
                    )
            self.schedule()

    def schedule(self):
        """Schedule the next run based on a simple threshold check.

        Using the reqeusted polling_interval and the current load we determine
        an appropriate time to wait before running another iteration.  The next
        iteration will occur after
        (1.0 - LOAD_CUR/LOAD_THRESH)*POLL + LOAD_CUR/LOAD_THRESH seconds have
        passed.

        """

        load_ratio = os.getloadavg()[0]/float(self.learner["load_threshold"])

        sleep_time = max(
                (1.0 - load_ratio)*float(
                    self.arguments.polling_interval) + load_ratio,
                1.0)

        logging.info("Current Sleep Time: %s", int(sleep_time))

        signal.alarm(int(sleep_time))
        signal.pause()

