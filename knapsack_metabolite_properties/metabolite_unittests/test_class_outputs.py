import os
import unittest

import pandas as pd
from pkg_resources import resource_filename

from knapsack_metabolite_properties.alkaloid_classes import get_class_information_dict, \
    get_alkaloid_classes_from_metabolites

input_test_dir = resource_filename(__name__, 'test_inputs')
test_output_dir = resource_filename(__name__, 'test_outputs')


class MyTestCase(unittest.TestCase):

    def test_alkaloid_check(self):
        class_t_dict = get_class_information_dict()

        self.assertIn('Quinine', class_t_dict['Quinoline'])
        self.assertNotIn('Quinine', class_t_dict['MIA'])

        self.assertIn('Polyneuridine', class_t_dict['MIA'])
        self.assertNotIn('Polyneuridine', class_t_dict['Quinoline'])

    def test_class_information(self):
        # check overlaps
        class_t_dict = get_class_information_dict()
        for alk_class in class_t_dict:
            for alk_class2 in class_t_dict:
                if alk_class2 != alk_class:
                    for metabolite1 in class_t_dict[alk_class]:
                        self.assertNotIn(metabolite1, class_t_dict[alk_class2],
                                         msg=f'{metabolite1}:{alk_class}:{alk_class2}')

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
