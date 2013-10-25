# Copyright (C) 2013 by Alex Brandt <alunduil@alunduil.com>
#
# pmort is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

from crumbs import Parameters

CONFIGURATION_DIRECTORY = os.path.join(os.path.sep, 'etc', 'pmort')

PARAMETERS = Parameters(conflict_handler = 'resolve')

PARAMETERS.add_parameter(
        group = 'pmort',
        options = [ '--configuration-file-path', '-c' ],
        default = os.path.join(CONFIGURATION_DIRECTORY, 'pmort.ini'),
        help = \
                'Location of the configuration file to search for pmort ' \
                'parameters.  Default: %(default)s'
        )

PARAMETERS.parse(only_known = True)

PARAMETERS.add_configuration_file(PARAMETERS['pmort.configuration_file_path'])
