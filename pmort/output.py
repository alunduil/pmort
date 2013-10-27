# Copyright (C) 2013 by Alex Brandt <alunduil@alunduil.com>
#
# pmort is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import sys
import datetime
import os

from pmort.parameters import PARAMETERS

logger = logging.getLogger(__name__)

def write_output(name, output):
    '''Write the output of the given name to the appropriate location.

    Execute the following list of items around a given collection source:

    * record output in logging directory
    * flush the output from this collector
    * create a current symlink if logging directory isn't '-'

    The directory that will be written to is configurable but the collector name
    and current datetime are added as subdirectories to hold specific run
    information.  Output will be written to (for example)
    /var/spool/pmort/20130123223723/collector.log.

    Arguments
    ---------

    :``name``:   Name of the item whose output we're writing.
    :``output``: Output we're writing.

    '''

    logging.info('writing %s', name)

    output_fh = sys.stdout
    if not PARAMETERS['pmort.output_directory'].startswith('-'):
        now = datetime.now()

        output_directory = os.path.join(PARAMETERS['pmort.output_directory'], now.strftime('%Y$m$d%H%M%S'))

        if not os.access(output_directory, os.W_OK):
            os.mkdir(output_directory)

        output_fh = open(os.path.join(output_directory, name + '.log'), 'w')

    logger.info('writing to %s', output_fh.name)

    output_fh.write(output)
    output_fh.flush()

    if output_fh != sys.stdout:
        output_fh.close()

        logging.info('create current symlink')

        target = os.path.join(output_directory.rsplit('/', 1), 'current')
        source = output_directory

        logging.info('%s → %s', source, target)

        if os.access(target, os.W_OK):
            os.remove(target)

        os.symlink(source, target)
