# Copyright (C) 2013 by Alex Brandt <alunduil@alunduil.com>
#
# pmort is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import os

from pmort.collectors import COLLECTORS

logger = logging.getLogger(__name__)

def load_average_collector():
    '''Collector—Load Average'''

    return ', '.join([ str(_) for _ in os.getloadavg() ]) + '\n'

COLLECTORS['load_average'] = load_average_collector

if __name__ == '__main__':
    print(load_average_collector())
