import os.path
import unittest

import pandas as pd
from automatchnames import COL_NAMES
from pkg_resources import resource_filename

from cleaning import filter_out_ranks

_inputs_path = resource_filename(__name__, 'test_inputs')


class MyTestCase(unittest.TestCase):
    def test_filter_out_ranks(self):
        t_df = pd.read_csv(os.path.join(_inputs_path, 'unlabelled.csv'))
        filtered = filter_out_ranks(t_df)
        self.assertGreater(len(filtered.index), 0)
        self.assertEqual(filtered[COL_NAMES['acc_rank']].unique(), ['Species'])


if __name__ == '__main__':
    unittest.main()
