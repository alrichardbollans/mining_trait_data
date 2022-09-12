import os.path
import unittest

import pandas as pd
from automatchnames import COL_NAMES
from pkg_resources import resource_filename

from cleaning import filter_out_ranks, generate_temp_output_file_paths, merge_columns, merge_on_accepted_id, \
    compile_hits

_inputs_path = resource_filename(__name__, 'test_inputs')


class MyTestCase(unittest.TestCase):
    def test_filter_out_ranks(self):
        t_df = pd.read_csv(os.path.join(_inputs_path, 'unlabelled.csv'))
        filtered = filter_out_ranks(t_df)
        self.assertGreater(len(filtered.index), 0)
        self.assertEqual(filtered[COL_NAMES['acc_rank']].unique(), ['Species'])

    def test_merge_columns(self):
        t_df = pd.read_csv(os.path.join(_inputs_path, 'to_merge.csv'))
        merged = merge_columns(t_df, 'auto_merged', [COL_NAMES['acc_name'], COL_NAMES['acc_id']])
        pd.testing.assert_series_equal(merged['auto_merged'], t_df['Merged'], check_names=False)

    def test_merge_on_accepted_id(self):
        merged_df = pd.read_csv(os.path.join(_inputs_path, 'id_merged.csv'))
        one_df = pd.read_csv(os.path.join(_inputs_path, 'to_merge_id1.csv'))
        two_df = pd.read_csv(os.path.join(_inputs_path, 'to_merge_id2.csv'))
        automerged = merge_on_accepted_id(one_df, two_df)
        pd.testing.assert_frame_equal(merged_df, automerged)

    def test_compile_hits(self):
        merged_df = pd.read_csv(os.path.join(_inputs_path, 'list_plants_with_alkaloids.csv'))

        one_df = pd.read_csv(os.path.join(_inputs_path, 'powo_alkaloids_accepted.csv'))
        two_df = pd.read_csv(os.path.join(_inputs_path, 'rub_apocs_alkaloid_hits.csv'))
        compile_hits([one_df, two_df], os.path.join(_inputs_path, 'output_compiled.csv'))
        automerged = pd.read_csv(os.path.join(_inputs_path, 'output_compiled.csv'))
        pd.testing.assert_frame_equal(merged_df, automerged)


if __name__ == '__main__':
    unittest.main()
