import os.path
import unittest

import pandas as pd

from pkg_resources import resource_filename

from data_compilation_methods import filter_out_ranks, generate_temp_output_file_paths, compile_hits, COL_NAMES, single_source_col, \
    compiled_sources_col
from data_compilation_methods.compiling_datasets import _merge_snippets_of_repeated_taxa, _merge_columns, _merge_on_accepted_id

_inputs_path = resource_filename(__name__, 'test_inputs')
_outputs_path = resource_filename(__name__, 'test_outputs')


class MyTestCase(unittest.TestCase):

    def test_multiple_sources(self):
        cornell_hits = pd.read_csv(os.path.join(_inputs_path, 'cornell_accepted.csv'))
        wiki_hits = pd.read_csv(os.path.join(_inputs_path, 'wiki_poisons_accepted.csv'))
        powo_hits = pd.read_csv(os.path.join(_inputs_path, 'powo_poisons_accepted.csv'))

        compile_hits(
            [powo_hits, wiki_hits, cornell_hits],
            os.path.join(_outputs_path, 'output_poisons_compiled.csv'))

        auto_compiled = pd.read_csv(os.path.join(_outputs_path, 'output_poisons_compiled.csv'))
        compiled = pd.read_csv(os.path.join(_inputs_path, 'output_poisons_compiled.csv'))

        diff = pd.concat([compiled,auto_compiled])[['powo_Snippet']].drop_duplicates(keep=False)
        print(diff)
        pd.testing.assert_frame_equal(compiled, auto_compiled)

    def test_repeated_sources(self):
        cornell_hits = pd.read_csv(os.path.join(_inputs_path, 'cornell_accepted.csv'))
        wiki_hits = pd.read_csv(os.path.join(_inputs_path, 'wiki_poisons_accepted.csv'))
        powo_hits = pd.read_csv(os.path.join(_inputs_path, 'powo_poisons_accepted.csv'))

        compile_hits(
            [powo_hits, wiki_hits, cornell_hits, cornell_hits, wiki_hits],
            os.path.join(_outputs_path, 'output_poisons_repeated_compiled.csv'))

        auto_compiled = pd.read_csv(os.path.join(_outputs_path, 'output_poisons_repeated_compiled.csv'))
        compiled = pd.read_csv(os.path.join(_inputs_path, 'output_poisons_compiled.csv'))
        diff = pd.concat([compiled,auto_compiled])[['powo_Snippet']].drop_duplicates(keep=False)
        print(diff)
        pd.testing.assert_frame_equal(compiled, auto_compiled)

    def test_filter_out_ranks(self):
        t_df = pd.read_csv(os.path.join(_inputs_path, 'unlabelled.csv'))
        filtered = filter_out_ranks(t_df)
        self.assertGreater(len(filtered.index), 0)
        self.assertEqual(filtered[COL_NAMES['acc_rank']].unique(), ['Species'])

    def test_merge_columns(self):
        t_df = pd.read_csv(os.path.join(_inputs_path, 'to_merge.csv'))
        merged = _merge_columns(t_df, 'auto_merged', [COL_NAMES['acc_name'], COL_NAMES['acc_id']])
        pd.testing.assert_series_equal(merged['auto_merged'], t_df['Merged'], check_names=False)

    def test_merge_on_accepted_id(self):
        merged_df = pd.read_csv(os.path.join(_inputs_path, 'id_merged.csv'))
        one_df = pd.read_csv(os.path.join(_inputs_path, 'to_merge_id1.csv'))
        merged_dfs = one_df.copy()
        merged_dfs[compiled_sources_col] = merged_dfs[[single_source_col]].values.tolist()

        merged_dfs = merged_dfs.drop(columns=[single_source_col])

        two_df = pd.read_csv(os.path.join(_inputs_path, 'to_merge_id2.csv'))
        automerged = _merge_on_accepted_id(merged_dfs, two_df)
        pd.testing.assert_series_equal(merged_df['Compiled_Sources'].astype(str),
                                       automerged['Compiled_Sources'].astype(str))

    def test_compile_hits(self):
        merged_df = pd.read_csv(os.path.join(_inputs_path, 'list_plants_with_alkaloids.csv'))

        one_df = pd.read_csv(os.path.join(_inputs_path, 'powo_alkaloids_accepted.csv'))
        two_df = pd.read_csv(os.path.join(_inputs_path, 'rub_apocs_alkaloid_hits.csv'))
        compile_hits([one_df, two_df], os.path.join(_outputs_path, 'output_compiled.csv'))
        automerged = pd.read_csv(os.path.join(_outputs_path, 'output_compiled.csv'))
        pd.testing.assert_frame_equal(merged_df, automerged)

    def test_compile_snippets(self):
        poison_df = pd.read_csv(os.path.join(_inputs_path, 'poisons.csv'))
        autocompiled = _merge_snippets_of_repeated_taxa(poison_df)
        compiled = pd.read_csv(os.path.join(_inputs_path, 'poisons_compiled_snippets.csv'))

        pd.testing.assert_frame_equal(compiled, autocompiled)


if __name__ == '__main__':
    unittest.main()
