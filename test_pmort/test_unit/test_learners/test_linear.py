# Copyright (C) 2013 by Alex Brandt <alunduil@alunduil.com>
#
# pmort is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import unittest
import mock

from pmort.parameters import PARAMETERS
from pmort.learners.linear import LinearLearner

class LinearLearnerTimeTest(unittest.TestCase):
    def setUp(self):
        _ = mock.patch.object(LinearLearner, 'learn')
        mock_learn = _.start()
        self.addCleanup(_.stop)

        _ = mock.patch.object(LinearLearner, 'learned_maximum_load', new_callable = mock.PropertyMock)
        self.mock_max_load = _.start()
        self.addCleanup(_.stop)

        _ = mock.patch('pmort.learners.linear.os.getloadavg')
        self.mock_load = _.start()
        self.addCleanup(_.stop)

        _ = mock.patch('pmort.learners.linear.PARAMETERS')
        mock_parameters = _.start()
        self.addCleanup(_.stop)

        mock_parameters.__getitem__.side_effect = lambda _: {
                'learner.minimum_interval': 1,
                'learner.maximum_interval': 600,
                }[_]

        self.l = LinearLearner()

    def test_linear_times(self):
        '''Linear Times'''

        loads = (
                (0.0, 1.0, 600),
                (0.5, 1.0, 300.5),
                (1.0, 1.0, 1),
                (1.0, 0.5, 1),
                )

        for load in loads:
            self.mock_load.return_value = (load[0],)
            self.mock_max_load.return_value = load[1]

            self.assertEqual(load[2], self.l.time())
