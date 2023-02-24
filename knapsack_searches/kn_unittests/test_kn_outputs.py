import os.path
import unittest

import pandas as pd
from pkg_resources import resource_filename
from tqdm import tqdm
from wcvp_download import wcvp_accepted_columns, get_all_taxa
from wcvp_name_matching import get_accepted_info_from_names_in_column

from knapsack_searches import get_metabolites_for_taxon, get_metabolites_in_family, kn_metabolite_name_column

input_test_dir = resource_filename(__name__, 'test_inputs')
test_output_dir = resource_filename(__name__, 'test_outputs')


class MyTestCase(unittest.TestCase):

    def taxon_test(self, name, known_vals):
        table = get_metabolites_for_taxon(name)

        metabolites = table[kn_metabolite_name_column].values.tolist()

        self.assertEqual(metabolites, known_vals)

    def test_no_info(self):
        apoc_no_info_searches = ['XXX', 'Mandevilla', 'Tromotriche', 'Orthanthera', 'Bustelma', 'Cystostemma',
                                 'Widgrenia', 'Dactylostelma', 'Gothofreda', 'Oxystelma', 'Rhombonema',
                                 'Pattalias', 'Macbridea', 'Vadulia', 'Pentacyphus', 'Pentatropis',
                                 'Acustelma']

        all_genera_df = pd.DataFrame()
        for i in tqdm(range(len(apoc_no_info_searches)), desc="Searching genera in Knapsack…", ascii=False,
                      ncols=80):
            genus = apoc_no_info_searches[i]
            genus_table = get_metabolites_for_taxon(genus)
            if len(genus_table.index) > 0:
                all_genera_df = pd.concat([all_genera_df, genus_table])
        if len(all_genera_df.index) > 0:
            acc_df = get_accepted_info_from_names_in_column(all_genera_df, 'Organism',
                                                            families_of_interest=['Apocynaceae'])
            acc_df.to_csv(os.path.join(test_output_dir, 'apoc_no_info.csv'))
            acc_df = acc_df.dropna(subset=[wcvp_accepted_columns['id']])

            self.assertEqual(len(acc_df.index), 0)

        rub_no_info = ['Thouarsiora', 'Bemsetia', 'Tsiangia', 'Schetti', 'Taligalea', 'Zuccarinia', 'Jackia',
                       'Janotia', 'Jovetia', 'Joosia', 'Gouldia', 'Neobaumannia', 'Dentillaria', 'Kohautia']

        all_genera_df = pd.DataFrame()
        for i in tqdm(range(len(rub_no_info)), desc="Searching genera in Knapsack…", ascii=False,
                      ncols=80):
            genus = rub_no_info[i]
            genus_table = get_metabolites_for_taxon(genus)
            if len(genus_table.index) > 0:
                all_genera_df = pd.concat([all_genera_df, genus_table])
        if len(all_genera_df.index) > 0:
            acc_df = get_accepted_info_from_names_in_column(all_genera_df, 'Organism',
                                                            families_of_interest=['Rubiaceae'])
            acc_df.to_csv(os.path.join(test_output_dir, 'rub_no_info.csv'))
            acc_df = acc_df.dropna(subset=[wcvp_accepted_columns['id']])

            self.assertEqual(len(acc_df.index), 0)

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
        # logan = get_metabolites_in_family('Loganiaceae', output_csv=os.path.join(test_output_dir,
        #                                                                          'loganiaceae_metabolites.csv'))
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

    def test_all_genera_searched_for(self):

        # metas_df = get_metabolites_in_family('Rubiaceae',output_csv=os.path.join(test_output_dir, 'Rubiaceae_kn_search.csv'))
        metas_df = pd.read_csv(os.path.join(test_output_dir, 'Rubiaceae_kn_search.csv'))

        rub_genera = get_all_taxa(families_of_interest=['Rubiaceae'], ranks=['genus'], accepted=True)[
            wcvp_accepted_columns['name']].values
        rub_no_info = ['Thouarsiora', 'Bemsetia', 'Tsiangia', 'Schetti', 'Taligalea', 'Zuccarinia', 'Jackia',
                       'Janotia', 'Jovetia', 'Joosia', 'Gouldia', 'Neobaumannia', 'Dentillaria', 'Kohautia']

        for genus in rub_genera:
            if genus not in rub_no_info:
                self.assertIn(genus, metas_df['accepted_parent'].values)


if __name__ == '__main__':
    unittest.main()
