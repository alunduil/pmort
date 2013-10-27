# Copyright (C) 2013 by Alex Brandt <alunduil@alunduil.com>
#
# pmort is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import os
import sys

from crumbs import Parameters

CONFIGURATION_DIRECTORY = os.path.join(os.path.sep, 'etc', 'pmort')

PARAMETERS = Parameters(conflict_handler = 'resolve')

PARAMETERS.add_parameter(
        group = 'pmort',
        options = [ '--configuration-file-path', '-c' ],
        metavar = 'FILE',
        default = os.path.join(CONFIGURATION_DIRECTORY, 'pmort.ini'),
        help = \
                'Location of the configuration file to search for pmort ' \
                'parameters.  Default: %(default)s'
        )

PARAMETERS.add_parameter(
        options = [ '--output-directory', '-o' ],
        group = 'pmort',
        metavar = 'DIR',
        default = os.path.join(os.path.sep, 'var', 'spool', sys.argv[0]),
        help = \
                'Specifies the output directory that the collection output ' \
                'is collected into.'
        )

PARAMETERS.add_parameter(
        options = [ '--cache-directory' ],
        group = 'pmort',
        metavar = 'DIR',
        default = os.path.join(os.path.sep, 'var', 'cache', sys.argv[0]),
        help = \
                'Specifies the output directory for any learned ' \
                'information.  Default: %(default)s'
        )

PARAMETERS.add_parameter(
        options = [ '--configuration-file-path' ],
        group = 'logging',
        metavar = 'FILE',
        default = os.path.join(CONFIGURATION_DIRECTORY, 'logging.ini'),
        help = \
                'Specifies the file path for the logging configuration file. ' \
        )

PARAMETERS.parse(only_known = True)

PARAMETERS.add_configuration_file(PARAMETERS['pmort.configuration_file_path'])
