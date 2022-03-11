import os.path
import unittest

import pandas as pd

from soil_vars import add_property_means


class MyTestCase(unittest.TestCase):
    def test_nitrogen(self):
        occ_df = pd.read_csv(os.path.join('test_inputs/AcokantheralaevigataAgathisanthemumbojeri.csv'))
        nitrogen_df = add_property_means(occ_df, 'nitrogen')

        correct_nitrogen_df = pd.read_csv(
            os.path.join('test_inputs/AcokantheralaevigataAgathisanthemumbojeri_w_nitrogren.csv'))

        pd.testing.assert_series_equal(nitrogen_df['nitrogen'], correct_nitrogen_df['nitrogen'])


if __name__ == '__main__':
    unittest.main()
