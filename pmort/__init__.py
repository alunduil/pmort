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

"""pmort is a post-mortem analysis suite.

This differs from other utilties in the following ways:

    * Dynamic polling intervals (users specify a maximum polling unit)
    * Switches to parallel implementations under high system duress
    * Makes every attempt to gather as much information as possible in disaster
      scanerios

pmort runs as a daemon to provide lightweight processing of its monitors
(plugins) but can be run as a single iteration (adding to the logging of
information by the daemon.  This leads to potential cases such as calling pmort
when monit notices a condition is met (to capture more than simply polled
events), running it with cron jobs to capture more information while long
running crons are executing and many more that might be dreamed up.

Once the daemon (or process) is running, several things are going to be
captured (and to particular regions).  The important pieces of pmort's
architecture are outlined below:

    * Runs monitors (plugins) that log to individual files for easy reference
    * Logs to a particular configurable directory (defaults to /var/log/pmort)
    * Individual runs log to directories such as /var/log/pmort/20120506123434/
    * Learns certains facts about the system to provide better monitoring
    * Learned facts are stored in the configurable cache directory

"""

