import os
import unittest

import numpy as np
import pandas as pd
from pkg_resources import resource_filename

from name_matching_cleaning import id_lookup_wcvp, get_accepted_info_from_ids_in_column, \
    find_best_matches_from_multiples, get_knms_matches_and_accepted_info_from_names_in_column, \
    get_accepted_info_from_names_in_column
from taxa_lists.get_taxa_from_wcvp import get_all_taxa

wcvp_taxa = get_all_taxa()
unittest_inputs = resource_filename(__name__, 'test_inputs')
unittest_outputs = resource_filename(__name__, 'test_outputs')


class MyTestCase(unittest.TestCase):

    def test_id_lookup_wcvp(self):
        cap_dict = id_lookup_wcvp(wcvp_taxa, '44583-2')
        self.assertEqual(cap_dict['Accepted_Name'], 'Capirona macrophylla')
        self.assertEqual(cap_dict['Accepted_ID'], '77210192-1')
        self.assertEqual(cap_dict['Accepted_Rank'], 'Species')
        self.assertEqual(cap_dict['Accepted_Species'], 'Capirona macrophylla')
        self.assertEqual(cap_dict['Accepted_Species_ID'], '77210192-1')

        cap_dict = id_lookup_wcvp(wcvp_taxa, '77210192-1')
        self.assertEqual(cap_dict['Accepted_Name'], 'Capirona macrophylla')
        self.assertEqual(cap_dict['Accepted_ID'], '77210192-1')
        self.assertEqual(cap_dict['Accepted_Rank'], 'Species')
        self.assertEqual(cap_dict['Accepted_Species'], 'Capirona macrophylla')
        self.assertEqual(cap_dict['Accepted_Species_ID'], '77210192-1')

        cap_dict = id_lookup_wcvp(wcvp_taxa, '2217-1')
        self.assertEqual(cap_dict['Accepted_Name'], 'Aspidosperma')
        self.assertEqual(cap_dict['Accepted_ID'], '2217-1')
        self.assertEqual(cap_dict['Accepted_Rank'], 'Genus')
        self.assertTrue(np.isnan(cap_dict['Accepted_Species']))
        self.assertTrue(np.isnan(cap_dict['Accepted_Species_ID']))

        cap_dict = id_lookup_wcvp(wcvp_taxa, '41511-1')
        self.assertEqual(cap_dict['Accepted_Name'], 'Aspidosperma')
        self.assertEqual(cap_dict['Accepted_ID'], '2217-1')
        self.assertEqual(cap_dict['Accepted_Rank'], 'Genus')
        self.assertTrue(np.isnan(cap_dict['Accepted_Species']))
        self.assertTrue(np.isnan(cap_dict['Accepted_Species_ID']))

        cap_dict = id_lookup_wcvp(wcvp_taxa, '35260-1')
        self.assertEqual(cap_dict['Accepted_Name'], 'Richardia')
        self.assertEqual(cap_dict['Accepted_ID'], '35260-1')
        self.assertEqual(cap_dict['Accepted_Rank'], 'Genus')
        self.assertTrue(np.isnan(cap_dict['Accepted_Species']))
        self.assertTrue(np.isnan(cap_dict['Accepted_Species_ID']))

        cap_dict = id_lookup_wcvp(wcvp_taxa, '30000008-2')
        self.assertTrue(np.isnan(cap_dict['Accepted_Name']))
        self.assertTrue(np.isnan(cap_dict['Accepted_ID']))
        self.assertTrue(np.isnan(cap_dict['Accepted_Rank']))
        self.assertTrue(np.isnan(cap_dict['Accepted_Species']))
        self.assertTrue(np.isnan(cap_dict['Accepted_Species_ID']))

        cap_dict = id_lookup_wcvp(wcvp_taxa, '30000422-2')
        self.assertTrue(np.isnan(cap_dict['Accepted_Name']))
        self.assertTrue(np.isnan(cap_dict['Accepted_ID']))
        self.assertTrue(np.isnan(cap_dict['Accepted_Rank']))
        self.assertTrue(np.isnan(cap_dict['Accepted_Species']))
        self.assertTrue(np.isnan(cap_dict['Accepted_Species_ID']))

        cap_dict = id_lookup_wcvp(wcvp_taxa, 'abc')
        self.assertTrue(np.isnan(cap_dict['Accepted_Name']))
        self.assertTrue(np.isnan(cap_dict['Accepted_ID']))
        self.assertTrue(np.isnan(cap_dict['Accepted_Rank']))
        self.assertTrue(np.isnan(cap_dict['Accepted_Species']))
        self.assertTrue(np.isnan(cap_dict['Accepted_Species_ID']))

        cap_dict = id_lookup_wcvp(wcvp_taxa, '')
        self.assertTrue(np.isnan(cap_dict['Accepted_Name']))
        self.assertTrue(np.isnan(cap_dict['Accepted_ID']))
        self.assertTrue(np.isnan(cap_dict['Accepted_Rank']))
        self.assertTrue(np.isnan(cap_dict['Accepted_Species']))
        self.assertTrue(np.isnan(cap_dict['Accepted_Species_ID']))

        cap_dict = id_lookup_wcvp(wcvp_taxa, ' ')
        self.assertTrue(np.isnan(cap_dict['Accepted_Name']))
        self.assertTrue(np.isnan(cap_dict['Accepted_ID']))
        self.assertTrue(np.isnan(cap_dict['Accepted_Rank']))
        self.assertTrue(np.isnan(cap_dict['Accepted_Species']))
        self.assertTrue(np.isnan(cap_dict['Accepted_Species_ID']))

        cap_dict = id_lookup_wcvp(wcvp_taxa, np.nan)
        self.assertTrue(np.isnan(cap_dict['Accepted_Name']))
        self.assertTrue(np.isnan(cap_dict['Accepted_ID']))
        self.assertTrue(np.isnan(cap_dict['Accepted_Rank']))
        self.assertTrue(np.isnan(cap_dict['Accepted_Species']))
        self.assertTrue(np.isnan(cap_dict['Accepted_Species_ID']))

    def test_get_accepted_info_from_ids_in_column(self):
        unstandardised = pd.read_csv(os.path.join(unittest_inputs, 'powo_medicinal.csv'), index_col=False)
        standardised = pd.read_csv(os.path.join(unittest_inputs, 'powo_medicinal_cleaned.csv'), index_col=False)

        unstandardised.rename(columns={'Unnamed: 0': 'X'}, inplace=True)

        x = get_accepted_info_from_ids_in_column(unstandardised, 'fqId')

        print(standardised.columns)
        print(x.columns)
        pd.testing.assert_frame_equal(standardised, x)

        garbage = get_accepted_info_from_ids_in_column(unstandardised, 'powo_Snippet')
        unstandardised['Accepted_Name'] = np.nan
        unstandardised['Accepted_ID'] = np.nan
        unstandardised['Accepted_Rank'] = np.nan
        unstandardised['Accepted_Species'] = np.nan
        unstandardised['Accepted_Species_ID'] = np.nan

        pd.testing.assert_frame_equal(unstandardised, garbage)

    def test_find_best_matches(self):
        multiple_names = {
            'submitted': ['Asclepias curassavica', 'Asclepias curassavica', 'Condylocarpon', 'Condylocarpon',
                          'Condylocarpon'],
            'match_state': ['multiple_matches', 'multiple_matches', 'multiple_matches', 'multiple_matches',
                            'multiple_matches'],
            'ipni_id': ['urn:lsid:ipni.org:names:94213-1', 'urn:lsid:ipni.org:names:94212-1',
                        'urn:lsid:ipni.org:names:39836-1', 'urn:lsid:ipni.org:names:328988-2',
                        'urn:lsid:ipni.org:names:11637-1'],
            'matched_name': ['Asclepias curassavica Sp. Pl.: 215 (1753) L. 1753',
                             'Asclepias curassavica Abh. Königl. Ges. Wiss. Göttingen 19: 159 (1874) Griseb. 1874',
                             'Condylocarpus Gen. Pl. Umbell., ed. 2: 202 (1816) Hoffm. 1816',
                             'Condylocarpon Mém. Mus. Hist. Nat. 8: 119 (1822) Desf. 1822',
                             'Condylocarpus Descr. Pinus, ed. 3, 1: 120 (1832) Salisb. ex Lamb. 1832']}

        multiple_names_df = pd.DataFrame(multiple_names)
        multiple_match_records = find_best_matches_from_multiples(multiple_names_df)

        self.assertEqual(
            len(multiple_match_records[multiple_match_records['submitted'] == 'Asclepias curassavica'].index), 1)
        self.assertEqual(len(multiple_match_records[multiple_match_records['submitted'] == 'Condylocarpon'].index), 1)

        self.assertEqual(
            multiple_match_records.loc[multiple_match_records['submitted'] == 'Condylocarpon', 'Accepted_ID'].iloc[0],
            '328988-2')
        self.assertEqual(
            multiple_match_records.loc[
                multiple_match_records['submitted'] == 'Asclepias curassavica', 'Accepted_ID'].iloc[0],
            '94213-1')

        self.assertEqual(
            multiple_match_records.loc[multiple_match_records['submitted'] == 'Condylocarpon', 'Accepted_Name'].iloc[0],
            'Condylocarpon')
        self.assertEqual(
            multiple_match_records.loc[
                multiple_match_records['submitted'] == 'Asclepias curassavica', 'Accepted_Name'].iloc[0],
            'Asclepias curassavica')

    def test_get_matched_names_and_accepted_info_from_names_in_column(self):
        synonym_list = pd.read_csv(os.path.join(unittest_inputs, 'synonym_list.csv'))
        x = get_knms_matches_and_accepted_info_from_names_in_column(synonym_list, 'syn')
        x.to_csv(os.path.join(unittest_outputs, 'test_output3.csv'))
        self.assertTrue(len(x['Accepted_Name'].values.tolist()) == len(synonym_list['syn'].values.tolist()))
        self.assertListEqual(x['Accepted_Name'].values.tolist(), x['Know_acc_name'].values.tolist())

        genera_list = pd.read_csv(os.path.join(unittest_inputs, 'genera_list.csv'))
        x = get_knms_matches_and_accepted_info_from_names_in_column(genera_list, 'Unlabelled')
        x.to_csv(os.path.join(unittest_outputs, 'test_output1.csv'))
        self.assertListEqual(x['Unlabelled'].values.tolist(), x['Accepted_Name'].values.tolist())
        self.assertListEqual(sorted(genera_list['Unlabelled'].values.tolist()),
                             sorted(x['Accepted_Name'].values.tolist()))

        #
        species_list = pd.read_csv(os.path.join(unittest_inputs, 'species_list.csv'))
        x = get_knms_matches_and_accepted_info_from_names_in_column(species_list, 'Labelled')
        x.to_csv(os.path.join(unittest_outputs, 'test_output2.csv'))
        self.assertListEqual(x['Labelled'].values.tolist(), x['Accepted_Name'].values.tolist())
        self.assertListEqual(sorted(species_list['Labelled'].values.tolist()),
                             sorted(x['Accepted_Name'].values.tolist()))

    def test_get_accepted_info_from_names_in_column(self):
        synonym_list = pd.read_csv(os.path.join(unittest_inputs, 'synonym_list.csv'))
        x = get_accepted_info_from_names_in_column(synonym_list, 'syn')
        x.to_csv(os.path.join(unittest_outputs, 'test_output4.csv'))
        self.assertTrue(len(x['Accepted_Name'].values.tolist()) == len(synonym_list['syn'].values.tolist()))
        self.assertListEqual(x['Accepted_Name'].values.tolist(), x['Know_acc_name'].values.tolist())

        genera_list = pd.read_csv(os.path.join(unittest_inputs, 'genera_list.csv'))
        x = get_accepted_info_from_names_in_column(genera_list, 'Unlabelled')
        x.to_csv(os.path.join(unittest_outputs, 'test_output5.csv'))
        self.assertListEqual(x['Unlabelled'].values.tolist(), x['Accepted_Name'].values.tolist())
        self.assertListEqual(sorted(genera_list['Unlabelled'].values.tolist()),
                             sorted(x['Accepted_Name'].values.tolist()))

        #
        species_list = pd.read_csv(os.path.join(unittest_inputs, 'species_list.csv'))
        x = get_accepted_info_from_names_in_column(species_list, 'Labelled')
        x.to_csv(os.path.join(unittest_outputs, 'test_output6.csv'))
        self.assertListEqual(x['Labelled'].values.tolist(), x['Accepted_Name'].values.tolist())
        self.assertListEqual(sorted(species_list['Labelled'].values.tolist()),
                             sorted(x['Accepted_Name'].values.tolist()))


if __name__ == '__main__':
    unittest.main()