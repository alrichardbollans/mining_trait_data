import unittest

import pandas as pd

from common_name_vars import output_common_names_csv
from unit_test_methods import confirming_hits


class MyTestCase(unittest.TestCase):
    def test_hits(self):
        p = confirming_hits()
        hits = pd.read_csv(output_common_names_csv, index_col=0)
        p.confirm_hit('Catharanthus roseus', hits)
        p.confirm_no_hit('atharanthus roseus', hits)
        p.confirm_powo_hit('Catharanthus roseus', hits)

        p.confirm_powo_hit('Gonzalagunia panamensis', hits)
        p.confirm_no_hit('Tocoyena pittieri', hits)

if __name__ == '__main__':
    unittest.main()
