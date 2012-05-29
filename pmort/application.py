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
import daemon
import lockfile
import signal
import pwd
import grp
import os
import threading

import pmort.helpers as helpers

from pmort.plugins import PostMortemPlugins

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

        if self.arguments.debug:
            helpers.debug({
                "self.arguments.daemonize":self.arguments.daemonize,
                })

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

        if self.arguments.debug:
            helpers.debug({
                "ret":ret,
                })

        return ret

    def learn(self):
        if os.getloadavg()[0] > self.load_threshold:
            file_ = open(os.path.join(self.arguments.cache, "load_threshold"), "w")
            file_.write(unicode(os.getloadavg()[0]))
            file_.close()

    def iteration(self):
        verbosity = {
                "verbose": self.arguments.verbose,
                "debug": self.arguments.debug,
                }

        if os.getloadavg()[0] > self.load_threshold:
            self.parallel_iteration(verbosity)
        else:
            self.serial_iteration(verbosity)
        self.learn()

    def serial_iteration(self, verbosity):
        for plugin in PostMortemPlugins(**verbosity):
            self._single_iteration()

    def _single_iteration(self, plugin):
        if self.arguments.output:
            if self.arguments.output.startswith("-"):
                output = sys.stdout
            else:
                output = open(self.arguments.output, "w")
        else:
            now = datetime.now()
            log_path = os.path.join(self.arguments.log_directory, now.strftime("%Y%m%d%H%M%S"))
            if not os.access(log_path, os.W_OK):
                os.mkdir(log_path)
            output = open(os.path.join(log_path, plugin + ".log", "w"))

        plugin.log(output = output)

    def parallel_iteration(self, verbosity):
        for plugin in PostMortemPlugins(**verbosity):
            thread = threading.Thread(target = self._single_iteration, name = plugin, args = (self, plugin))
            thread.start()

        if self.arguments.debug:
            helpers.debug({
                "threading.active_count()":threading.active_count(),
                "threading.enumerate()":threading.enumerate(),
                })

    def daemonize(self):

        context = daemon.DaemonContext(
                working_directory = '/var/log/psmort',
                umask = 0o002,
                pidfile = lockfile.FileLock(self.arguments.pidfile),
                )

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

        if self.arguments.chroot:
            context.chroot = self.arguments.chroot

        context.uid = pwd.getpwnam(self.arguments.uid).pw_uid
        context.gid = grp.getgrnam(self.arguments.gid).gr_gid

        with context:
            self.schedule()
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

        # --daemonize, -d
        help_list = [
                "Specifies that the application should run as a daemon rather ",
                "than just one run of each plugin.",
                ]
        self.parser.add_argument("--daemonize", "-d", action = "store_true",
                default = False, help = "".join(help_list))

        # --poll_seconds, -s
        help_list = [
                "Specifies the polling period for subsequent runs of the ",
                "plugged in monitors.  The time, S, specified is assumed to ",
                "be seconds.",
                ]
        self.parser.add_argument("--poll_seconds", "-s", type = int,
                metavar = "S", help = "".join(help_list))

        # --pidfile, -p
        help_list = [
                "Specified the location of the process id file.  Defaults to ",
                "/var/run/pmort.pid.",
                ]
        self.parser.add_argument("--pidfile", "-p", 
                default = "/var/run/pmort.pid", help = "".join(help_list))

        # --configfile, -c
        help_list = [
                "Specifies the location of the configuration file.  Defaults ",
                "to /etc/pmort/pmort.conf.",
                ]
        self.parser.add_argument("--configfile", "-c",
                default = "/etc/pmort/pmort.conf", help = "".join(help_list))

        # --chroot, -r
        help_list = [
                "Specifies a directoy to chroot into after starting.",
                ]
        self.parser.add_argument("--chroot", "-r", default = None,
                help = "".join(help_list))

        # --uid, -u
        help_list = [
                "Specifies the username the daemon should run as.",
                ]
        self.parser.add_argument("--uid", "-u", default = "pmort",
                help = "".join(help_list))

        # --gid, -g
        help_list = [
                "Specifies the groupname the daemon should run as.",
                ]
        self.parser.add_argument("--gid", "-g", default = "pmort",
                help = "".join(help_list))

        # --cache, -C
        help_list = [
                "Specifies an alternative directory to learn items into.  ",
                "Defaults to /var/cache/pmort.",
                ]
        self.parser.add_argument("--cache", "-C", default = "/var/cache/pmort",
                help = "".join(help_list))

        return self._parser

