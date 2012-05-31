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

"""pmort.learning is a self-contained knowledge store for pmort's facts.

This system provides a dict-like object that can be used to update known facts
or to query for the current value of known facts.

"""

import os
import logging

class Learner(object):
    """Knowledge store for pmort's basic facts.

    Given a directory to store knowledge (cache) items in, this small helper
    simplifies storage and querying of relevant facts.  This simplified API
    allows the storage mechanism to be changed out at will as well.

    The API provided by this class has only two components:
      1. Retrieving Facts
      2. Updating Facts

    This class is stateless (interacting with disk to preserve anything that
    might be updated on subsequent passes).  This class is not currently thread
    safe.

    TODO Make this class thread safe.

    This class is idempotent as far as usage goes (it doesn't matter how
    frequently something is learned) and allows for us to utilize this object
    in disparate execution locations without worrying about common state.

    Examples:

      * Retrieving Facts
          Learner(cache_dir)["fact_name"]
      * Updating Facts
          Learner(cache_dir).learn()

    """

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

        if os.access(os.path.join(self._cache, file_), os.R_OK):
            with open(os.path.join(self._cache, file_), "r") as file_:
                ret = file_.readline()

        return ret

    def learn(self):
        """Records facts to a persistent state on disk.

        Records facts into specific files in the cache directory.  Doesn't
        have any parameters to modify behaviour.  All locations are set
        relative to the cache directory.  Simply call this method to update
        pmort's knowledge about relevant facts about the system.

        """

        for name, fact in self._facts.iteritems():
            logging.debug("Fact: %s", name)
            logging.debug("Current Value: %s", fact["value"]())
            logging.debug("Current Fact: %s", self[name])
            logging.debug("Comparison: %s", cmp(fact["value"](), self[name]))
            logging.debug("Expected Comparison: %s", fact["cmp"])

            if cmp(fact["value"](), self[name]) == fact["cmp"]:
                logging.info("Updating fact, %s, to %s from %s", name,
                        fact["value"](), self[name])

                file_ = name 
                if "file" in fact:
                    file_ = fact["file"]

                with open(os.path.join(self._cache, file_), "w") as file_:
                    file_.write(unicode(fact["value"]()))

