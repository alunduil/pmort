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
import os

class Learner(object):
    def __init__(self, cache):
        self._cache = cache
        self._facts = {
                "load_threshold": {
                    "default": 0.1,
                    "value": lambda : os.getloadavg()[0],
                    "cmp": 1,
                    },
                }
    
    def __getitem__(self, fact):
        if fact not in self._facts:
            raise KeyError(fact)

        ret = self._facts[fact]["default"]

        file_ = fact
        if "file" in self._facts[fact]:
            file_ = self._facts[fact]["file"]

        with open(os.path.join(self._cache, file_), "r") as file_:
            ret = file_.readline()

        return ret

    def learn(self):
        for name, fact in self._facts:
            if cmp(fact["value"](), self[fact]) == fact["cmp"]:
                logging.info("Updating fact, %s, to %s from %s", fact, fact["value"](), self[fact])

                file_ = fact
                if "file" in self._facts[fact]:
                    file_ = self._facts[fact]["file"]

                with open(os.path.join(self._cache, file_), "w") as file_:
                    file_.write(unicode(fact["value"]()))

