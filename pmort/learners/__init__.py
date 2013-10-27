# Copyright (C) 2013 by Alex Brandt <alunduil@alunduil.com>
#
# pmort is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

__all__ = [
        'LEARNERS',
        ]

import logging
import os
import itertools
import importlib

from pmort.parameters import PARAMETERS

logger = logging.getLogger(__name__)

PARAMETERS.add_parameter(
        options = [ '--active', ],
        group = 'learner',
        default = 'linear', # TODO Switch to predictive.
        help = \
                'The learner algorithm to utilize for determining inter-run ' \
                'timings.  Default %(default)s'
        )

PARAMETERS.add_parameter(
        options = [ '--maximum-interval', ],
        group = 'learner',
        default = 600,
        type = int,
        help = \
                'Set the maximum time between collections by %(prog)s.  This ' \
                'specifies the maximum number of seconds between ' \
                'collections.  Default %(default)s'
        )

LEARNERS = {}

module_basename = __name__
logger.info('loading submodules of %s', module_basename)

directory = os.path.dirname(__file__)
logger.info('loading learners from %s', directory)

filenames = itertools.chain(*[ [ os.path.join(_[0], filename) for filename in _[2] ] for _ in os.walk(directory) if len(_[2]) ])

module_names = []
for filename in filenames:
    if filename.endswith('.py'):
        _ = filename

        _ = _.replace(directory + '/', '')
        _ = _.replace('__init__.py', '')
        _ = _.replace('.py', '')

        if len(_):
            module_names.append(module_basename + '.' + _)

logger.debug('modules found: %s', list(module_names))

for module_name in module_names:
    logger.info('loading learner %s', module_name)

    try:
        importlib.import_module(module_name)
    except ImportError as e:
        logger.warning('failed loading %s', module_name)
        logger.exception(e)
    else:
        logger.info('successfully loaded %s', module_name)
