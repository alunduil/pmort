# Copyright (C) 2013 by Alex Brandt <alunduil@alunduil.com>
#
# pmort is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import os

from pmort.parameters import PARAMETERS
from pmort.learners import LEARNERS

logger = logging.getLogger(__name__)

class LinearLearner(object):
    @property
    def cache_file_name(self):
        return os.path.join(PARAMETERS['pmort.cache_directory'], 'learned', 'maximum_one_minute_load.txt')

    @property
    def learned_maximum_load(self):
        maximum_load = 0.0

        with open(self.cache_file_name, 'r') as max_one_minute_load_fh:
            maximum_load = float(max_one_minute_load_fh.read().strip())

        return maximum_load

    def learn(self):
        '''Record the current system items required to make a future decision.

        This records (in the pmort cache directory) any system information it
        will need in order to provide the next sleep time.  A crude mechanism
        but effective none-the-less.

        For this learner, we only need to capture the current system load if
        it's larger than the currently recorded value.

        '''

        logger.info('learn maximum one minute load')

        current_loadavg = os.getloadavg()[0]

        logger.debug('current one minute load: %s')
        logger.debug('learned maximum load: %s')

        if current_loadavg > self.learned_maximum_load:
            with open(self.cache_file_name, 'w') as max_one_minute_load_fh:
                max_one_minute_load_fh.write(current_loadavg)

    def time(self):
        '''Return the calculated amount of time to sleep.

        Using the algorithm decided upon and the learned information, this
        calculates and returns an appropriate amount of time to sleep.

        Returns
        -------

        An appropriate amount of time to sleep.

        '''

        self.learn()

        scale = - os.getloadavg()[0] / self.learned_maximum_load

        logger.debug('linear scale: %s', scale)

        return max(scale * ( PARAMETERS['learner.maximum_interval'] - PARAMETERS['learner.minimum_interval'] ) + PARAMETERS['learner.maximum_interval'], PARAMETERS['learner.minimum_interval'])

LEARNERS['linear'] = LinearLearner()
