import os.path
import unittest

import pandas as pd
from pkg_resources import resource_filename
from wcvpy.wcvp_download import wcvp_accepted_columns

from data_compilation_methods import compile_hits, compiled_sources_col

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

        auto_compiled = pd.read_csv(os.path.join(_outputs_path, 'output_poisons_compiled.csv'), index_col=0)
        compiled = pd.read_csv(os.path.join(_inputs_path, 'output_poisons_compiled.csv'), index_col=0)

        pd.testing.assert_frame_equal(compiled.sort_values(by=wcvp_accepted_columns['name']).reset_index(drop=True)[compiled.columns],
                                      auto_compiled.sort_values(by=wcvp_accepted_columns['name']).reset_index(drop=True)[compiled.columns])

    def test_compile_same_hits(self):
        one_df = pd.read_csv(os.path.join(_inputs_path, 'hairs_powo_accepted.csv'), index_col=0)
        two_df = pd.read_csv(os.path.join(_inputs_path, 'hairs_powo_accepted.csv'), index_col=0)
        compile_hits([one_df, two_df], os.path.join(_outputs_path, 'output_compiled_hairs.csv'))
        automerged = pd.read_csv(os.path.join(_outputs_path, 'output_compiled_hairs.csv'), index_col=0)

        OUTPUT_COL_NAMES = [wcvp_accepted_columns['name'], wcvp_accepted_columns['name_w_author'],
                            wcvp_accepted_columns['ipni_id'],
                            wcvp_accepted_columns['rank'],
                            wcvp_accepted_columns['species'],
                            wcvp_accepted_columns['species_w_author'],
                            wcvp_accepted_columns['species_ipni_id'],
                            wcvp_accepted_columns['family'],
                            compiled_sources_col]
        # Put name columns at begining
        start_cols = OUTPUT_COL_NAMES[:]
        start_cols.remove(compiled_sources_col)

        one_df[compiled_sources_col] = one_df['Source'].apply(lambda x: str([x]))
        merged_df = one_df[start_cols+ [compiled_sources_col]]
        merged_df =merged_df.drop_duplicates(subset=wcvp_accepted_columns['name_w_author'])
        merged_df = merged_df.dropna(subset=[wcvp_accepted_columns['name_w_author']])

        merged_df = merged_df.sort_values(by=wcvp_accepted_columns['name']).reset_index(drop=True)
        pd.testing.assert_frame_equal(merged_df[merged_df.columns], automerged[merged_df.columns])

    def test_adding_hits(self):
        one_df = pd.read_csv(os.path.join(_inputs_path, 'hairs_powo_accepted.csv'), index_col=0).head(100)
        two_df = pd.read_csv(os.path.join(_inputs_path, 'hairs_powo_accepted.csv'), index_col=0).tail(3026)
        compile_hits([one_df, two_df], os.path.join(_outputs_path, 'output_compiled_hairs.csv'))
        automerged = pd.read_csv(os.path.join(_outputs_path, 'output_compiled_hairs.csv'), index_col=0)

        OUTPUT_COL_NAMES = [wcvp_accepted_columns['name'], wcvp_accepted_columns['name_w_author'],
                            wcvp_accepted_columns['ipni_id'],
                            wcvp_accepted_columns['rank'],
                            wcvp_accepted_columns['species'],
                            wcvp_accepted_columns['species_w_author'],
                            wcvp_accepted_columns['species_ipni_id'],
                            wcvp_accepted_columns['family'],
                            compiled_sources_col]
        # Put name columns at begining
        start_cols = OUTPUT_COL_NAMES[:]
        start_cols.remove(compiled_sources_col)
        merged_df = pd.concat([one_df,two_df])
        merged_df[compiled_sources_col] = merged_df['Source'].apply(lambda x: str([x]))
        merged_df = merged_df[start_cols + [compiled_sources_col]]
        merged_df = merged_df.drop_duplicates(subset=wcvp_accepted_columns['name_w_author'])
        merged_df = merged_df.dropna(subset=[wcvp_accepted_columns['name_w_author']])

        merged_df = merged_df.sort_values(by=wcvp_accepted_columns['name']).reset_index(drop=True)
        pd.testing.assert_frame_equal(merged_df[merged_df.columns], automerged[merged_df.columns])


if __name__ == '__main__':
    unittest.main()
