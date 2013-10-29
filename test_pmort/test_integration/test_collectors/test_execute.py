# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 by Alex Brandt <alunduil@alunduil.com>
#
# pmort is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import unittest
import stat
import os
import shutil
import functools

from pmort.collectors.execute import find_scripts

logger = logging.getLogger(__name__)

class FindScriptsTest(unittest.TestCase):
    def setUp(self):
        file_contents = (
                {
                    'name': 'found_1.sh',
                    'add_permissions': 0O111,
                    'contents':
                            '#!/bin/bash\n'
                            'echo found'
                    },
                {
                    'name': 'not_found_1.sh',
                    'add_permissions': 0O000,
                    'contents':
                            '#!/bin/bash\n'
                            'echo not_found'
                    },
                {
                    'name': 'not_found_1.sh',
                    'add_permissions': 0O111,
                    'contents':
                            'echo not_found'
                    },
                )

        self.directory = os.path.join(os.path.sep, 'tmp', 'test_pmort')

        os.makedirs(self.directory)
        self.addCleanup(functools.partial(shutil.rmtree, self.directory))

        for file_content in file_contents:
            file_path = os.path.join(self.directory, file_content['name'])

            logger.info('writing %s', file_path)

            with open(file_path, 'w') as fh:
                fh.write(file_content['contents'])
                fh.flush()

            logger.debug('permissions: %s', oct(os.stat(file_path)[stat.ST_MODE] | file_content['add_permissions']))

            os.chmod(file_path, os.stat(file_path)[stat.ST_MODE] | file_content['add_permissions'])

        self.expected = [
                [ '/bin/bash', os.path.join(self.directory, 'found_1.sh'), ]
                ]

    def test_find_scripts(self):
        '''find_scripts'''

        self.assertEqual(self.expected, find_scripts(self.directory))
