import os.path
import unittest

import numpy as np
import pandas as pd
from pkg_resources import resource_filename
from wcvp_download import wcvp_accepted_columns

from metabolite_properties import is_alkaloid_from_name_formulae_or_class, get_alkaloids_from_metabolites, \
    get_knapsack_antimalarial_metabolite_hits_for_taxa, get_knapsack_antimalarial_metabolites, \
    get_knapsack_inactive_antimalarial_metabolites, \
    get_knapsack_inactive_antimalarial_metabolite_hits_for_taxa, \
    get_N_containing_from_metabolites
from knapsack_searches import kn_metabolite_name_column

input_test_dir = resource_filename(__name__, 'test_inputs')
test_output_dir = resource_filename(__name__, 'test_outputs')


class MyTestCase(unittest.TestCase):

    def test_alkaloid_check(self):
        should_be_alks = [['Kopsanone', ''], ['kopsanone', 'XX11dasd'], ['Kopsanone', 1],
                          [' Hygrine', 'VVVV'], [' Cuscohygrine', '111'], ['7-O-Acetylsalutaridinol', 'XXXX'],
                          ['madeupalkine', 'N'], ['madeup1alkine', 'n']]
        for a in should_be_alks:
            self.assertNotEqual(is_alkaloid_from_name_formulae_or_class(a[0], [a[1]]), 'False', msg=a)

        shouldntbealks = [['madeupalkine', 'CH3'], ['quinone', 'N']]

        for a in shouldntbealks:
            self.assertEqual(is_alkaloid_from_name_formulae_or_class(a[0], [a[1]]), 'False', msg=a)


    def test_antimal_metas(self):
        metabs = get_knapsack_antimalarial_metabolites()
        should_be_antimal = ['Emodin', '(-)-Lycorine', 'Canthin-6-one', 'Afrormosin', 'Afromosin',
                             "Castanin",
                             "7-Hydroxy-6,4'-dimethoxyisoflavone"]

        for m in should_be_antimal:
            self.assertIn(m, metabs)

        for m in ['Heriguard', '3-O-Caffeoylquinic acid', 'Heriguard']:
            self.assertNotIn(m, metabs)

    def test_inactiveantimal_metas(self):
        metabs = get_knapsack_inactive_antimalarial_metabolites()

        should_be_antimal = ['3-O-Caffeoylquinic acid', 'Heriguard']
        for m in should_be_antimal:
            self.assertIn(m, metabs)


if __name__ == '__main__':
    unittest.main()
