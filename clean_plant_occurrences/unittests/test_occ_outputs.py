import os
import unittest

import pandas as pd
from pkg_resources import resource_filename

from clean_plant_occurrences import final_occurrence_output_csv, clean_occurrences_by_tdwg_regions

input_test_dir = resource_filename(__name__, 'test_inputs')
test_output_dir = resource_filename(__name__, 'test_outputs')

cleaned_output_df = pd.read_csv(final_occurrence_output_csv)
# cleaned_output_df = pd.read_csv('../test.csv')


class MyTestCase(unittest.TestCase):

    def test_bad_records(self):
        bad_records = pd.read_csv(os.path.join(input_test_dir, 'occs_which_should_be_removed.csv'))
        cleaned = clean_occurrences_by_tdwg_regions(bad_records,
                                                    output_csv=os.path.join(test_output_dir, 'should_be_empty.csv'))
        self.assertEqual(len(cleaned.index), 0)

        for id in bad_records['gbifID'].values:
            self.assertNotIn(id, cleaned_output_df['gbifID'].values)

    def test_clean_output(self):
        def test_examples(occ_df: pd.DataFrame, tag: str):
            dups = occ_df[occ_df.duplicated(subset=['gbifID'])]
            self.assertEqual(len(dups.index), 0)

            # Coord uncertainty 20000
            print('coord uncertainty clean')
            uncertain = occ_df[occ_df['coordinateUncertaintyInMeters'] > 20000]
            uncertain.to_csv(os.path.join(test_output_dir, tag + 'bad_coord_examples.csv'))
            # clim_occ_df = clim_occ_df[clim_occ_df['coordinateUncertaintyInMeters'] <= 20000]

            self.assertEqual(len(uncertain.index), 0)

            ## Years
            uncertain = occ_df[occ_df['year'] < 1945]
            uncertain.to_csv(os.path.join(test_output_dir, tag + 'bad_year_examples.csv'))
            self.assertEqual(len(uncertain.index), 0)
            ## 0 long and lat
            uncertain = occ_df[(occ_df['decimalLongitude'] == 0) & (occ_df['decimalLatitude'] == 0)]
            uncertain.to_csv(os.path.join(test_output_dir, tag + 'bad_zerolatlong_examples.csv'))
            self.assertEqual(len(uncertain.index), 0)
            uncertain = occ_df[(occ_df['decimalLongitude'] == occ_df['decimalLatitude'])]
            uncertain.to_csv(os.path.join(test_output_dir, 'bad_eqlatlong_examples.csv'))
            self.assertEqual(len(uncertain.index), 0)
            # na lat long
            uncertain = occ_df[(occ_df['decimalLongitude'].isna()) | (occ_df['decimalLatitude'].isna())]
            uncertain.to_csv(os.path.join(test_output_dir, tag + 'bad_nalatlong_examples.csv'))
            self.assertEqual(len(uncertain.index), 0)

            # na codes
            # uncertain = occ_df[(occ_df['countryCode'].isna())]
            # uncertain.to_csv(os.path.join(test_dir, tag+'bad_naccode_examples.csv'))

        test_examples(cleaned_output_df, '')

    # def test_native_introduced(self):
    #     native_occ_df = pd.read_csv(clean_native_occurences_with_clim_vars_csv)
    #     print(len(native_occ_df.index))
    #     introd_occ_df = pd.read_csv(clean_introd_occurences_with_clim_vars_csv)
    #     print(len(introd_occ_df.index))
    #
    #     occ_df = pd.concat([native_occ_df, introd_occ_df])
    #     dups = occ_df[occ_df['gbifID'].duplicated(keep="first")]
    #     print(dups)
    #     dups.to_csv(os.path.join(test_dir, 'introduced_natives.csv'))
    #     print(len(dups['fullname'].unique()))
    #     print(dups['fullname'].unique())
    #
    #     for taxa in dups['fullname'].unique():
    #         # Verify that it's not just all instances of specific taxa
    #         dups_taxa = dups[dups['fullname'] == taxa]
    #         native_taxa = native_occ_df[native_occ_df['fullname'] == taxa]
    #         int_taxa = introd_occ_df[introd_occ_df['fullname'] == taxa]
    #
    #         all_taxa = pd.concat([native_taxa, int_taxa]).drop_duplicates(subset=['gbifID'], keep='first')
    #
    #         if len(all_taxa) != len(dups_taxa):
    #             print(taxa)
    #             print(len(all_taxa))
    #             print(len(dups_taxa))
    #
    #     self.assertEqual(len(dups.index), 0)


if __name__ == '__main__':
    unittest.main()
