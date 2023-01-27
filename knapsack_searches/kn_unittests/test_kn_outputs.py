import os.path
import unittest

import pandas as pd
from pkg_resources import resource_filename
from wcvp_download import wcvp_accepted_columns

from knapsack_searches import get_metabolites_for_taxon, get_metabolites_in_family, kn_metabolite_name_column

input_test_dir = resource_filename(__name__, 'test_inputs')
test_output_dir = resource_filename(__name__, 'test_outputs')


class MyTestCase(unittest.TestCase):

    def taxon_test(self, name, known_vals):
        table = get_metabolites_for_taxon(name)

        metabolites = table[kn_metabolite_name_column].values.tolist()

        self.assertEqual(metabolites, known_vals)

    def test_meta_known_taxa(self):
        known_vals = ['(+)-Aspidospermidine', '(+)-Fendlerine', 'Alalakine', 'Aspidolimidine', 'Limaspermine',
                      'N-Acetylaspidospermidine']
        self.taxon_test('Aspidosperma album', known_vals)

        # Test some synonyms with vals
        self.taxon_test('Curarea', ['Isochondodendrine', 'Isochondodendrine', 'Isochondodendrine', 'Limacine',
                                    "(-)-Limacine 2'-beta-N-oxide", '(-)-Curine', '(-)-Krukovine',
                                    "(-)-Limacine 2'-alpha-N-oxide", '(-)-Limacine, 2-beta-N-oxide',
                                    '(+)-Candicusine', 'Limacusine'])

    def test_data_for_family(self):
        # logan = get_metabolites_in_family(['Loganiaceae'],output_csv=os.path.join(test_output_dir, 'loganiaceae_metabolites.csv'))
        logan = pd.read_csv(os.path.join(test_output_dir, 'loganiaceae_metabolites.csv'))

        lucida = logan[logan[wcvp_accepted_columns['name']] == 'Strychnos lucida'][
            kn_metabolite_name_column].values

        known_lucida_vals = ['Brucine', 'Strychnine', 'Acanthoside B', '3-O-Caffeoylquinic acid', 'Loganin',
                             'Adenosine', 'Loganate', 'Cantleyoside', 'Sylvestroside I', 'Sweroside',
                             'Tachioside', 'alpha-Colubrine', 'beta-Colubrine', 'Brucine N-oxide',
                             'Diaboline', 'Normacusine B', 'Pseudobrucine', 'Pseudostrychnine',
                             '11-Methoxydiaboline', '3,4-di-O-caffeoylquinic acid',
                             'Ligustrinoside', 'Picconioside I', 'Secoxyloganin', 'Staunoside C',
                             'Triplostoside A']

        for m in lucida:
            self.assertIn(m, known_lucida_vals, msg=m)

        for m in known_lucida_vals:
            self.assertIn(m, lucida, msg=m)


if __name__ == '__main__':
    unittest.main()
