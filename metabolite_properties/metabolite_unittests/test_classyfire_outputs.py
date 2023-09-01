import os.path
import unittest

import pandas as pd
from pkg_resources import resource_filename

from metabolite_properties import get_classyfire_classes_from_smiles, get_classyfire_classes_from_df

input_test_dir = resource_filename(__name__, 'test_inputs')
test_output_dir = resource_filename(__name__, 'test_outputs')


class MyTestCase(unittest.TestCase):

    def test_example_smiles(self):
        example_metabolites = pd.read_csv(os.path.join(input_test_dir, 'metabolite_example.csv'), index_col=0)

        smiles = example_metabolites['SMILES'].dropna()
        out_df = get_classyfire_classes_from_smiles(smiles, 'temp_outputs')
        out_df.to_csv(os.path.join(test_output_dir, 'classyfire_example.csv'))
        self.assertEqual(len(out_df.index), len(smiles.unique().tolist()))
        known_correct = pd.read_csv(os.path.join(input_test_dir, 'correct_classyfire_example.csv'), index_col=0)

        pd.testing.assert_frame_equal(out_df, known_correct)

    def test_example_df(self):
        example_metabolites = pd.read_csv(os.path.join(input_test_dir, 'metabolite_example.csv'), index_col=0)
        out_df = get_classyfire_classes_from_df(example_metabolites, 'SMILES', 'temp_outputs')
        out_df.to_csv(os.path.join(test_output_dir, 'classyfire_df_example.csv'))

        known_correct = pd.read_csv(os.path.join(input_test_dir, 'correct_classyfire_df_example.csv'), index_col=0)

        self.assertEqual(len(example_metabolites.index), len(out_df.index))

        pd.testing.assert_frame_equal(out_df.fillna('').drop(columns=['plant_name_id']), known_correct.fillna('').drop(columns=['plant_name_id']), )


if __name__ == '__main__':
    unittest.main()
