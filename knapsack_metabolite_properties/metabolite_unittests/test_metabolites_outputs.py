import os.path
import unittest

import pandas as pd
from pkg_resources import resource_filename
from wcvp_download import wcvp_accepted_columns

from knapsack_metabolite_properties import is_alkaloid, get_alkaloids_from_metabolites, \
    get_antimalarial_metabolite_hits_for_taxa, get_antimalarial_metabolites, \
    get_inactive_antimalarial_metabolites, get_inactive_antimalarial_metabolite_hits_for_taxa, \
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
            self.assertNotEqual(is_alkaloid(a[0], a[1]), 'False', msg=a)

        shouldntbealks = [['madeupalkine', 'CH3'], ['quinone', 'N']]

        for a in shouldntbealks:
            self.assertEqual(is_alkaloid(a[0], a[1]), 'False', msg=a)

    def test_alk_output(self):
        # logan = get_metabolites_in_family('Loganiaceae',os.path.join(test_output_dir, 'loganiaceae_metabolites.csv'))
        logan = pd.read_csv(os.path.join(test_output_dir, 'loganiaceae_metabolites.csv'))
        logan_alk_df = get_alkaloids_from_metabolites(logan, temp_output_csv=os.path.join(test_output_dir,
                                                                                          'logan_metabolites_w_alks.csv'),
                                                      output_csv=os.path.join(test_output_dir,
                                                                              'logan_metabolites_w_alks_final.csv'))

        lucida = logan_alk_df[logan_alk_df[wcvp_accepted_columns['name']] == 'Strychnos lucida'][
            kn_metabolite_name_column].values

        known_lucida_alks = ['Brucine', 'Strychnine',
                             'Adenosine',
                             'alpha-Colubrine', 'beta-Colubrine', 'Brucine N-oxide',
                             'Diaboline', 'Normacusine B', 'Pseudobrucine', 'Pseudostrychnine',
                             '11-Methoxydiaboline']

        for m in lucida:
            self.assertIn(m, known_lucida_alks, msg=m)

        for m in known_lucida_alks:
            self.assertIn(m, lucida, msg=m)

        n_containing = get_N_containing_from_metabolites(logan, output_csv=os.path.join(test_output_dir,
                                                                                        'logan_metabolites_w_N.csv'))
        n_formulae = n_containing[kn_metabolite_name_column].values
        alkaloid_formulae = logan_alk_df[kn_metabolite_name_column].values
        all_formulae = logan[kn_metabolite_name_column].values
        for alk in alkaloid_formulae:
            self.assertIn(alk, n_formulae)

        self.assertGreater(len(all_formulae), len(n_formulae))

    def test_antimal_metas(self):
        metabs = get_antimalarial_metabolites()
        should_be_antimal = ['Emodin', '(-)-Lycorine', 'Canthin-6-one', 'Afrormosin', 'Afromosin',
                             "Castanin",
                             "7-Hydroxy-6,4'-dimethoxyisoflavone"]
        for m in should_be_antimal:
            self.assertIn(m, metabs)

        for m in ['Heriguard']:
            self.assertNotIn(m, metabs)

    def test_inactiveantimal_metas(self):
        metabs = get_inactive_antimalarial_metabolites()
        should_be_antimal = ['3-O-Caffeoylquinic acid', 'Heriguard']
        for m in should_be_antimal:
            self.assertIn(m, metabs)

    def test_antimal_output(self):
        # logan = get_metabolites_in_family('Loganiaceae',outputcsv = os.path.join(test_output_dir, 'loganiaceae_metabolites.csv'))
        logan = pd.read_csv(os.path.join(test_output_dir, 'loganiaceae_metabolites.csv'))

        logan_antiplasm_df = get_antimalarial_metabolite_hits_for_taxa(logan, output_csv=os.path.join(test_output_dir,
                                                                                           'logan_antimal.csv'))

        lucida = \
            logan_antiplasm_df[logan_antiplasm_df[wcvp_accepted_columns['name']] == 'Strychnos usambarensis'][
                kn_metabolite_name_column].values

        known_lucida_antiplasm = ['Isostrychnopentamine']

        for m in lucida:
            self.assertIn(m, known_lucida_antiplasm, msg=m)

        for m in known_lucida_antiplasm:
            self.assertIn(m, lucida, msg=m)

    def test_inactiveantimal_output(self):
        # logan = get_metabolites_in_family('Loganiaceae',outputcsv = os.path.join(test_output_dir, 'loganiaceae_metabolites.csv'))
        logan = pd.read_csv(os.path.join(test_output_dir, 'loganiaceae_metabolites.csv'))

        logan_antiplasm_df = get_inactive_antimalarial_metabolite_hits_for_taxa(logan,
                                                                                output_csv=os.path.join(test_output_dir,
                                                                                             'logan_inacgtiveantimal.csv'))

        lucida = \
            logan_antiplasm_df[logan_antiplasm_df[wcvp_accepted_columns['name']] == 'Strychnos lucida'][
                kn_metabolite_name_column].values

        known_lucida_inactive_antiplasm = ['3-O-Caffeoylquinic acid']

        for m in lucida:
            self.assertIn(m, known_lucida_inactive_antiplasm, msg=m)

        for m in known_lucida_inactive_antiplasm:
            self.assertIn(m, lucida, msg=m)


if __name__ == '__main__':
    unittest.main()
