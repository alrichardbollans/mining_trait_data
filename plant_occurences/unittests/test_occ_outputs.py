import os
import unittest

import pandas as pd
from pkg_resources import resource_filename


class MyTestCase(unittest.TestCase):
    def test_something(self):
        test_dir = resource_filename(__name__, 'test_outputs')
        #
        plant_occ_dir = '/home/atp/Documents/work life/Kew/large folders/plant_occurence_vars/outputs/'
        sp_df = pd.read_csv(plant_occ_dir + 'cleaned_sp_occurences.csv')
        subsp_df = pd.read_csv(plant_occ_dir + 'cleaned_subsp_occurences.csv')
        var_df = pd.read_csv(plant_occ_dir + 'cleaned_vari_occurences.csv')

        def test_examples(occ_df):
            dups = occ_df[occ_df.duplicated(subset=['gbifID'])]
            print(dups)
            if len(dups.index) > 0:
                raise ValueError

            # Coord uncertainty 20000
            print('coord uncertainty clean')
            uncertain = occ_df[occ_df['coordinateUncertaintyInMeters'] > 20000]
            uncertain.to_csv(os.path.join(test_dir, 'bad_coord_examples.csv'))
            print(len(occ_df.index))
            # clim_occ_df = clim_occ_df[clim_occ_df['coordinateUncertaintyInMeters'] <= 20000]

            print(len(occ_df.index))

            ## Years
            uncertain = occ_df[occ_df['year'] < 1945]
            uncertain.to_csv(os.path.join(test_dir, 'bad_year_examples.csv'))
            self.assertEqual(len(uncertain.index), 0)
            ## 0 long and lat
            uncertain = occ_df[(occ_df['decimalLongitude'] == 0) & (occ_df['decimalLatitude'] == 0)]
            uncertain.to_csv(os.path.join(test_dir, 'bad_zerolatlong_examples.csv'))
            self.assertEqual(len(uncertain.index), 0)
            uncertain = occ_df[(occ_df['decimalLongitude'] == occ_df['decimalLatitude'])]
            uncertain.to_csv(os.path.join(test_dir, 'bad_eqlatlong_examples.csv'))
            self.assertEqual(len(uncertain.index), 0)
            # na lat long
            uncertain = occ_df[(occ_df['decimalLongitude'].isna()) | (occ_df['decimalLatitude'].isna())]
            uncertain.to_csv(os.path.join(test_dir, 'bad_nalatlong_examples.csv'))
            self.assertEqual(len(uncertain.index), 0)

            # na codes
            # uncertain = occ_df[(occ_df['countryCode'].isna())]
            # uncertain.to_csv(os.path.join(test_dir, 'bad_naccode_examples.csv'))

        test_examples(sp_df)
        test_examples(subsp_df)
        test_examples(var_df)


if __name__ == '__main__':
    unittest.main()
