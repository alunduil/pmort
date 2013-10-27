# Copyright (C) 2013 by Alex Brandt <alunduil@alunduil.com>
#
# pmort is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import os
import itertools
import subprocess

from pmort.parameters import PARAMETERS
from pmort.collectors import COLLECTORS
from pmort.output import write_output

logger = logging.getLogger(__name__)

def find_scripts(directory = os.path.dirname(__file__)):
    '''Find executable scripts (with shebang) in specified directory.

    Finds the scripts that can be executed in the specified directory.  Any
    scripts that are missing a shebang or the executable bit will be skipped.

    .. note::
        All python files are excluded as it's assumed that the main collector
        loading function will load those and run them.

    Arguments
    ---------

    :``directory``: Directory searched for executable scripts.

    Returns
    -------

    List of files matching the aforementioned criteria.

    '''

    filenames = itertools.chain(*[ [ os.path.join(_[0], filename) for filename in _[2] ] for _ in os.walk(directory) if len(_[2]) ])

    filenames = [ _ for _ in filenames if not _.endswith('.py') ]
    filenames = [ _ for _ in filenames if os.access(filename, os.X_OK) ]

    scripts = []

    for filename in filenames:
        with open(filename, 'r') as script_fh:
            _ = script_fh.readline().strip()

            if _.startswith('#!'):
                scripts.append(_[2:].split() + [ filename ])

    return scripts

def execute_collector():
    '''Collector—Execute'''

    logger.info('running execute')

    scripts = []
    scripts.extend(find_scripts())
    scripts.extend(find_scripts(PARAMETERS['collector_execute.directory']))

    errors = 0

    for script in scripts:
        logger.info('executing %s', script)

        try:
            output = subprocess.check_output(script)
        except subprocess.CalledProcessError as e:
            logger.warning('error in %s', script)
            logger.exception(e)

            errors += 1

            continue

        _ = ' '.join([ _.rsplit('/', 1)[-1] for _ in script ])
        write_output(_, output)

    return '\n'.join([
        'ran {0} execute plugins'.format(len(scripts)),
        '  {0} errors'.format(errors),
        ])

COLLECTORS['execute'] = execute_collector

if __name__ == '__main__':
    print(execute_collector())
