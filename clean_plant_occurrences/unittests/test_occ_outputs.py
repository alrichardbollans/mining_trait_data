import os
import unittest

import pandas as pd
from wcvp_name_matching import get_accepted_info_from_names_in_column
from pkg_resources import resource_filename

from clean_plant_occurrences import clean_occurrences_by_tdwg_regions
from clean_plant_occurrences.clean_by_tdwg_region import \
    _find_whether_occurrences_in_native_or_introduced_regions, get_tdwg_regions_for_occurrences

input_test_dir = resource_filename(__name__, 'test_inputs')
test_output_dir = resource_filename(__name__, 'test_outputs')


class MyTestCase(unittest.TestCase):

    def test_bad_records(self):
        bad_records = pd.read_csv(os.path.join(input_test_dir, 'occs_which_should_be_removed.csv'))
        native_cleaned = clean_occurrences_by_tdwg_regions(bad_records, name_column='fullname',
                                                           clean_by='native',
                                                           output_csv=os.path.join(test_output_dir,
                                                                                   'native_should_be_empty.csv'))
        self.assertEqual(len(native_cleaned.index), 0)

        both_cleaned = clean_occurrences_by_tdwg_regions(bad_records, name_column='fullname',
                                                         clean_by='both',
                                                         output_csv=os.path.join(test_output_dir,
                                                                                 'both_should_be_empty.csv'))
        self.assertEqual(len(both_cleaned.index), 0)

    def test_good_native_records(self):
        good_native_records = pd.read_csv(os.path.join(input_test_dir, 'native_ok.csv'))

        native_cleaned = clean_occurrences_by_tdwg_regions(good_native_records, name_column='fullname',
                                                           clean_by='native',
                                                           output_csv=os.path.join(test_output_dir,
                                                                                   'native_native.csv'),
                                                           remove_duplicate_records=False,
                                                           remove_duplicated_lat_long_at_rank='none')
        diff = good_native_records[~good_native_records['gbifID'].isin(native_cleaned['gbifID'])]
        print(diff['gbifID'])
        self.assertEqual(len(diff.index), 0)

        native_cleaned = clean_occurrences_by_tdwg_regions(good_native_records, name_column='fullname',
                                                           clean_by='both',
                                                           output_csv=os.path.join(test_output_dir,
                                                                                   'native_both.csv'),
                                                           remove_duplicate_records=False,
                                                           remove_duplicated_lat_long_at_rank='none')
        self.assertEqual(len(native_cleaned.index), len(good_native_records.index))

    def test_distributions_of_occs(self):
        dist_records = pd.read_csv(os.path.join(input_test_dir, 'occ_region_test.csv'))
        dist_records_with_tdwg = get_tdwg_regions_for_occurrences(dist_records)
        self.assertListEqual(dist_records_with_tdwg['known_region'].tolist(),
                             dist_records_with_tdwg['tdwg3_region'].tolist())

    def test_native_introduced_matching(self):
        dist_records = pd.read_csv(os.path.join(input_test_dir, 'occ_region_test.csv'))
        dist_records_wiht_acc_info = get_accepted_info_from_names_in_column(dist_records, 'fullname',
                                                                            families_of_interest=[
                                                                                'Apocynaceae',
                                                                                'Rubiaceae'])
        dist_records_with_tdwg = get_tdwg_regions_for_occurrences(dist_records_wiht_acc_info)
        dist_records_with_native_intro_info = _find_whether_occurrences_in_native_or_introduced_regions(
            dist_records_with_tdwg)
        dist_records_with_native_intro_info.to_csv(
            os.path.join(test_output_dir, 'tested_known_distributions.csv'))
        self.assertListEqual(dist_records_with_native_intro_info['known_native'].tolist(),
                             dist_records_with_native_intro_info['within_native'].tolist())

        self.assertListEqual(dist_records_with_native_intro_info['known_introd'].tolist(),
                             dist_records_with_native_intro_info['within_introduced'].tolist())

    def test_no_duplicates(self):
        good_native_records = pd.read_csv(os.path.join(input_test_dir, 'native_ok.csv'))
        native_cleaned = clean_occurrences_by_tdwg_regions(good_native_records, name_column='fullname',
                                                           clean_by='native',
                                                           output_csv=os.path.join(test_output_dir,
                                                                                   'native_native.csv'))
        bad_records_uncleaned = good_native_records[good_native_records['gbifID'].isin([9991, 9992, 9993])]
        self.assertEqual(len(bad_records_uncleaned), 3)

        bad_records = native_cleaned[native_cleaned['gbifID'].isin([9991, 9992])]
        self.assertEqual(len(bad_records), 0)


if __name__ == '__main__':
    unittest.main()
