import os.path
import unittest

import pandas as pd
from pkg_resources import resource_filename
from wcvp_download import wcvp_accepted_columns

from data_compilation_methods import compile_hits

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

    def test_compile_hits(self):
        merged_df = pd.read_csv(os.path.join(_inputs_path, 'list_plants_with_alkaloids.csv'))

        one_df = pd.read_csv(os.path.join(_inputs_path, 'powo_alkaloids_accepted.csv'))
        two_df = pd.read_csv(os.path.join(_inputs_path, 'rub_apocs_alkaloid_hits.csv'))
        compile_hits([one_df, two_df], os.path.join(_outputs_path, 'output_compiled.csv'))
        automerged = pd.read_csv(os.path.join(_outputs_path, 'output_compiled.csv'))
        pd.testing.assert_frame_equal(merged_df[merged_df.columns], automerged[merged_df.columns])


if __name__ == '__main__':
    unittest.main()
