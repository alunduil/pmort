# Copyright (C) 2013 by Alex Brandt <alunduil@alunduil.com>
#
# pmort is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

__all__ = [
        'COLLECTORS',
        ]

import logging
import os
import sys
import itertools
import importlib

from pmort.parameters import PARAMETERS
from pmort.parameters import CONFIGURATION_DIRECTORY

logger = logging.getLogger(__name__)

PARAMETERS.add_parameter(
        options = [ '--directory', ],
        group = 'collectors',
        default = os.path.join(CONFIGURATION_DIRECTORY, 'collectors.d'),
        help = \
                'Specify another directory to read collectors from.  The ' \
                'default directory is in the pmort configuration directory. ' \
                'Default: %(default)s'
        )

COLLECTORS = {}

# TODO Clean up this module …

def load_collectors(module_basename = __name__, directory = os.path.dirname(__file__), update_path = False):
    '''Load all modules (allowing collectors to register) in directory.

    All python modules in the given directory will be imported.  Collectors
    should be registering themselves by adding themselves to the COLLECTORS
    dict provided by this module.

    Parameters
    ----------

    :``module_basename``: Module name prefix for loaded modules. Defaults to
                          the name of this module.
    :``directory``:       Directory to recursively load python modules from.
                          Defaults to this module's directory.
    :``update_path``:     If True, the system path for modules is updated to
                          include ``directory``; otherwise, it is left alone.

    '''

    if update_path:
        update_path = bool(sys.path.count(directory))
        sys.path.append(directory)

    logger.info('loading submodules of %s', module_basename)
    directory = os.path.dirname(__file__)

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
        logger.info('loading collector %s', module_name)

        try:
            importlib.import_module(module_name)
        except ImportError as e:
            logger.warning('failed loading %s', module_name)
            logger.exception(e)
        else:
            logger.info('successfully loaded %s', module_name)

    if update_path:
        sys.path.remove(directory)

load_collectors()
if os.access(PARAMETERS['collectors.directory'], os.R_OK):
    load_collectors(module_basename = '', directory = PARAMETERS['collectors.directory'], update_path = True)
