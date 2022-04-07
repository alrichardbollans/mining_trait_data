import unittest

import pandas as pd

from alkaloid_vars import output_alkaloid_csv
from unit_test_methods import confirming_hits


class MyTestCase(unittest.TestCase):
    def test_hits(self):
        p = confirming_hits()
        hits = pd.read_csv(output_alkaloid_csv, index_col=0)
        p.confirm_hit('Catharanthus roseus', hits)
        p.confirm_no_hit('atharanthus roseus', hits)
        p.confirm_powo_hit('Catharanthus roseus', hits)
        p.confirm_knapsack_hit('Catharanthus roseus', hits,
                               ['Ajmalicine', 'Alstonine', 'hoerhammericine'])

        p.confirm_knapsack_hit('Psychotria malayana', hits)

        p.confirm_no_hit('Gonzalagunia panamensis', hits)


if __name__ == '__main__':
    unittest.main()
