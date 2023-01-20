import os
import unittest

from pkg_resources import resource_filename
from wcvp_download import get_all_taxa, wcvp_columns

from read_wep.parse_common_name_index import chars_not_appearing_in_wcvp, sources_of_apos_in_wcvp, \
    common_name_subheadings

input_test_dir = resource_filename(__name__, 'test_inputs')
test_output_dir = resource_filename(__name__, 'wcvp_outputs')

all_taxa = get_all_taxa()


class MyTestCase(unittest.TestCase):

    def test_common_names_in_chclist(self):
        for e in common_name_subheadings:
            print(e)
            e_df = all_taxa[all_taxa[wcvp_columns['name']].str.contains((r"\b{}\b".format(e)))]
            if len(e_df) > 0:
                e_df.to_csv(os.path.join(test_output_dir, e + '_wcvp.csv'))

    def test_chars(self):

        print(chars_not_appearing_in_wcvp)
        for e in ['weed']:
            print(e)
            e_df = all_taxa[all_taxa[wcvp_columns['name']].str.contains(e)]
            if len(e_df) > 0:
                e_df.to_csv(os.path.join(test_output_dir, e + '_wcvp.csv'))
            # self.assertEqual(len(e_df), 0, msg=f'{e} in wcvp')

        non_empties = ["'", '-']
        for e in non_empties:
            e_df = all_taxa[all_taxa[wcvp_columns['name']].str.contains(e)]
            if e == "'":
                for taxon in e_df[wcvp_columns['name']].values:
                    self.assertIn(taxon, sources_of_apos_in_wcvp)
            self.assertNotEqual(len(e), 0)
            e_df.to_csv(os.path.join(test_output_dir, e + '_wcvp.csv'))


if __name__ == '__main__':
    unittest.main()
