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

import ConfigParser

from pmort.parameters import PostMortemParameters

class PostMortemConfiguration(object):
    _config = None

    def __init__(self, configuration):
        defaults = dict([ (item["option_strings"][0][2:], item["default"]) for item in PostMortemParameters if "default" in item ])

        self._config = ConfigParser.SafeConfigParser(defaults)
        self._config.read(configuration)

    def __getattr__(self, key):
        return self._config.get("DEFAULT", key, raw = True)
