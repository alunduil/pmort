# Copyright (C) 2013 by Alex Brandt <alunduil@alunduil.com>
#
# pmort is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import unittest
import mock
import os
import functools
import shutil

from pmort.learners.linear import LinearLearner

class TestLinearLearnedMaximumLoad(unittest.TestCase):
    def setUp(self):
        self.directory = os.path.join(os.path.sep, 'tmp', 'test_pmort')

        os.makedirs(self.directory)
        self.addCleanup(functools.partial(shutil.rmtree, self.directory))

        _ = mock.patch.object(LinearLearner, 'cache_file_name', new_callable = mock.PropertyMock)
        mock_cache_file_name = _.start()
        self.addCleanup(_.stop)

        _ = os.path.join(self.directory, 'maximum_one_minute_load.txt')
        mock_cache_file_name.return_value = _

        with open(_, 'w') as fh:
            fh.write('4.56')
            fh.flush()

        self.l = LinearLearner()

    def test_learned_maximum_load(self):
        self.assertEqual(4.56, self.l.learned_maximum_load)
