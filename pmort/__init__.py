# Copyright (C) 2013 by Alex Brandt <alunduil@alunduil.com>
#
# pmort is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging

logging.basicConfig(level = getattr(logging, os.environ.get('PMORT_LOG_LEVEL', 'warn').upper()))

logger = logging.getLogger(__name__)

from pmort.parameters import PARAMETERS
from pmort.parameters import CONFIGURATION_DIRECTORY

from pmort.learners import LEARNERS
from pmort.collectors import COLLECTORS

PARAMETERS.add_parameter(
        options = [ '--configuration-file-path' ],
        group = 'logging',
        default = os.path.join(CONFIGURATION_DIRECTORY, 'logging.ini'),
        help = \
                'Specifies the file path for the logging configuration file. ' \
        )

PARAMETERS.add_parameter(
        options = [ '--output-directory' ],
        group = 'pmort',
        default = os.path.join(os.path.sep, 'var', 'spool', sys.argv[0]),
        help = \
                'Specifies the output directory that the collection output ' \
                'is collected into.'
        )

def write_collector_output(collector):
    '''Write the output of the given collector to the appropriate location.

    Execute the following list of items around a given collection source:

    * run collector and record output in logging directory
    * flush the output from this collector
    * create a current symlink if logging directory isn't '-'

    The directory that will be written to is configurable but the collector name
    and current datetime are added as subdirectories to hold specific run
    information.  Output will be written to (for example)
    /var/spool/pmort/20130123223723/collector.log.

    Arguments
    ---------

    :``collector``: Collector plugin being executed in this single iteration

    '''

    logging.info('running %s', collector)

    output = sys.stdout
    if not PARAMETERS['pmort.output_directory'].startswith('-')
        now = datetime.now()

        output_directory = os.path.join(PARAMETERS['pmort.output_directory'], now.strftime('%Y$m$d%H%M%S'))

        if not os.access(output_directory, os.W_OK):
            os.mkdir(output_directory)

        output = open(os.path.join(output_directory, str(collector) + '.log'), 'w')

    logger.info('writing to %s', output.name)

    output.write(collector.collect())
    output.flush()

    if output != sys.stdout:
        output.close()

        logging.info('create current symlink')

        target = os.path.join(output_directory.rsplit('/', 1), 'current')
        source = output.name

        logging.info('%s → %s', output_directory, target)

        if os.access(target, os.W_OK):
            os.remove(target)

        os.symlink(output_directory, target)

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

    learner = LEARNERS[PARAMETERS['learners.active']]

    # TODO Add last crash symlink.

    while True:
        for collector in COLLECTORS:
            thread = threading.Thread(target = collect, name = collector, args = (collector,))
            thread.start()

        logging.info('started %s threads', len(COLLECTORS))
        logging.info('active threads: %s', threading.active_count())

        learner.learn()

        signal.alarm(learner.time)
        signal.pause()

    return error
