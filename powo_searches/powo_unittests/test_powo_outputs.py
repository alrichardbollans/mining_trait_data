import os.path
import unittest

import pandas as pd
from pkg_resources import resource_filename

from powo_searches import search_powo

input_test_dir = resource_filename(__name__, 'test_inputs')
test_output_dir = resource_filename(__name__, 'test_outputs')


class MyTestCase(unittest.TestCase):

    def test_rub_alk_known_records(self):
        known_df = pd.read_csv(os.path.join(input_test_dir, 'powo_apoc_rub_alks.csv'))

        powo_output = os.path.join(test_output_dir, 'powo_apoc_rub_alkaloids.csv')
        search_powo(['alkaloid'], powo_output, families_of_interest=['Rubiaceae', 'Apocynaceae'],
                    filters=['species', 'infraspecies'])

        powo_output_df = pd.read_csv(powo_output)

        pd.testing.assert_frame_equal(powo_output_df, known_df)

    def test_known_records(self):
        known_df = pd.read_csv(os.path.join(input_test_dir, 'powo_alkaloids.csv'))

        powo_output = os.path.join(test_output_dir, 'powo_alkaloids.csv')
        search_powo(['alkaloid'], powo_output)

        powo_output_df = pd.read_csv(powo_output)

        pd.testing.assert_frame_equal(powo_output_df, known_df)

    def test_plurals(self):
        powo_output_s = os.path.join(test_output_dir, 'powo_poisons.csv')
        search_powo(['poisons'], powo_output_s, characteristics_to_search=['use'])
        powos_output_df = pd.read_csv(powo_output_s)

        powo_output = os.path.join(test_output_dir, 'powo_poison.csv')
        search_powo(['poison'], powo_output, characteristics_to_search=['use'])
        powo_output_df = pd.read_csv(powo_output)

        pd.testing.assert_frame_equal(powo_output_df, powos_output_df)

    def test_pagination(self):
        powo_output = os.path.join(test_output_dir, 'powo_poison_pages.csv')
        search_powo(['poison'], powo_output, characteristics_to_search=['use'])
        powo_output_df = pd.read_csv(powo_output)

        self.assertGreater(len(powo_output_df.index), 500)


if __name__ == '__main__':
    unittest.main()
