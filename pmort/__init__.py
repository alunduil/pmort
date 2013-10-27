# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 by Alex Brandt <alunduil@alunduil.com>
#
# pmort is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import os
import threading
import signal

logging.basicConfig(level = getattr(logging, os.environ.get('PMORT_LOG_LEVEL', 'warn').upper()))

logger = logging.getLogger(__name__)

from pmort.parameters import PARAMETERS
from pmort.learners import LEARNERS
from pmort.collectors import COLLECTORS
from pmort import output

def main():
    '''Main function for pmort.  Does all the things…sort of.

    Performs the basic loop of pmort but none of the normal daemon setup items.
    The basic logic in pmort is log all the things, sleep until the next time,
    and do it again.

    Returns
    -------

    1 if an error occurred; otherwise, it keeps running.

    '''

    error = 0

    global PARAMETERS
    PARAMETERS = PARAMETERS.parse()

    if os.access(PARAMETERS['logging.configuration_file_path'], os.R_OK):
        logging.config.fileConfig(PARAMETERS['logging.configuration_file_path'])

    # TODO Add last crash symlink.

    while True:
        for collector in COLLECTORS:
            thread = threading.Thread(
                    target = output.write_output,
                    group = 'pmort.collectors',
                    name = collector.__name__,
                    args = (collector.__name__.replace('_collector', ''), collector())
                    )
            thread.start()

        logging.info('started %s threads', len(COLLECTORS))
        logging.info('active threads: %s', threading.active_count())

        signal.alarm(LEARNERS[PARAMETERS['learner.active']].time())
        signal.pause()

    return error
