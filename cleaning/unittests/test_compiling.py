import os.path
import unittest

import pandas as pd

from pkg_resources import resource_filename

from cleaning import filter_out_ranks, generate_temp_output_file_paths, merge_columns, merge_on_accepted_id, \
    compile_hits, COL_NAMES

_inputs_path = resource_filename(__name__, 'test_inputs')
_outputs_path = resource_filename(__name__, 'test_outputs')


class MyTestCase(unittest.TestCase):

    def test_multiple_sources(self):
        cornell_hits = pd.read_csv(os.path.join(_inputs_path,'cornell_accepted.csv'))
        wiki_hits = pd.read_csv(os.path.join(_inputs_path,'wiki_poisons_accepted.csv'))
        powo_hits = pd.read_csv(os.path.join(_inputs_path,'powo_poisons_accepted.csv'))

        compile_hits(
            [ powo_hits, wiki_hits, cornell_hits],
            os.path.join(_outputs_path, 'output_poisons_compiled.csv'))

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
        merged_dfs = one_df.copy()
        merged_dfs[COL_NAMES['sources']] = merged_dfs[[COL_NAMES['single_source']]].values.tolist()

        merged_dfs = merged_dfs.drop(columns=[COL_NAMES['single_source']])

        two_df = pd.read_csv(os.path.join(_inputs_path, 'to_merge_id2.csv'))
        automerged = merge_on_accepted_id(merged_dfs, two_df)
        pd.testing.assert_series_equal(merged_df['Compiled_Sources'].astype(str), automerged['Compiled_Sources'].astype(str))

    def test_compile_hits(self):
        merged_df = pd.read_csv(os.path.join(_inputs_path, 'list_plants_with_alkaloids.csv'))

        one_df = pd.read_csv(os.path.join(_inputs_path, 'powo_alkaloids_accepted.csv'))
        two_df = pd.read_csv(os.path.join(_inputs_path, 'rub_apocs_alkaloid_hits.csv'))
        compile_hits([one_df, two_df], os.path.join(_inputs_path, 'output_compiled.csv'))
        automerged = pd.read_csv(os.path.join(_inputs_path, 'output_compiled.csv'))
        pd.testing.assert_frame_equal(merged_df, automerged)


if __name__ == '__main__':
    unittest.main()
