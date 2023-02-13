import os
import unittest

import pandas as pd
from pkg_resources import resource_filename

from knapsack_metabolite_properties.alkaloid_classes import get_class_information_dict, \
    get_alkaloid_classes_from_metabolites, alkaloid_class_from_metabolite

input_test_dir = resource_filename(__name__, 'test_inputs')
test_output_dir = resource_filename(__name__, 'test_outputs')


class MyTestCase(unittest.TestCase):

    def test_alkaloid_check(self):
        class_t_dict = get_class_information_dict()

        self.assertIn('quinoline', class_t_dict['quinine'])
        self.assertIn('mia', class_t_dict['polyneuridine'])
        self.assertNotIn('mia', class_t_dict['quinine'])
        self.assertNotIn('quinoline', class_t_dict['polyneuridine'])

    def test_metabolite_check(self):
        self.assertEqual(alkaloid_class_from_metabolite('Theobromine'),'indole')
        self.assertEqual(alkaloid_class_from_metabolite('THEObromine'),'indole')
        self.assertEqual(alkaloid_class_from_metabolite('(+)-THEObromine'),'indole')
        self.assertEqual(alkaloid_class_from_metabolite('(-)-THEObromine'),'indole')
        self.assertEqual(alkaloid_class_from_metabolite('O-(2-Pyrrolylcarbonyl)-virgiline'),'quinolizidine;pyrrolidine')

    def test_class_information(self):
        # check hierarchies
        class_t_dict = get_class_information_dict()
        for metabolite in class_t_dict:
            classes = class_t_dict[metabolite].split(';')

            if 'MIA' in classes:
                self.assertIn('indole', classes)
                self.assertIn('monoterpene', classes)


    def test_class_data(self):
        # logan = get_metabolites_in_family(['Loganiaceae'],os.path.join(test_output_dir, 'loganiaceae_metabolites.csv'))
        logan = pd.read_csv(os.path.join(test_output_dir, 'loganiaceae_metabolites.csv'), index_col=0)
        get_alkaloid_classes_from_metabolites(logan, output_csv=os.path.join(test_output_dir,
                                                                             'logan_alk_classes.csv'))

        logan = pd.read_csv(os.path.join(test_output_dir, 'logan_metabolites_w_alks_final.csv'), index_col=0)
        get_alkaloid_classes_from_metabolites(logan, output_csv=os.path.join(test_output_dir,
                                                                             'logan_alk_classes_known_alks.csv'))


if __name__ == '__main__':
    unittest.main()
