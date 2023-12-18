import unittest

import pandas as pd
from wcvp_download import wcvp_accepted_columns

from data_compilation_methods import compiled_sources_col


class confirming_hits(unittest.TestCase):
    
    def confirm_hit(self, taxa: str, output_hits: pd.DataFrame):

        self.assertIn(taxa, output_hits[wcvp_accepted_columns['name']].values.tolist())

        dup_hits_df = output_hits[output_hits.duplicated(subset=[wcvp_accepted_columns['name']], keep=False)]
        if len(dup_hits_df) > 0:
            raise ValueError(
                f'Duplicate hits found these should have been merged')

    def confirm_no_hit(self, taxa: str, output_hits: pd.DataFrame):

        self.assertNotIn(taxa, output_hits[wcvp_accepted_columns['name']].values.tolist())

    def confirm_powo_hit(self, taxa: str, output_hits: pd.DataFrame):

        self.assertIn('POWO', output_hits[output_hits[wcvp_accepted_columns['name']] == taxa][
            compiled_sources_col].values[0])

    def confirm_knapsack_hit(self, taxa: str, output_hits: pd.DataFrame):

        self.assertIn('KNApSAcK', output_hits[output_hits[wcvp_accepted_columns['name']] == taxa][
            compiled_sources_col].values[0])

    def confirm_knapsack_metas_hit(self, taxa: str, temp_output_hits: pd.DataFrame, metas):
        temp_output_hits_kn = temp_output_hits[temp_output_hits['Source']=='KNApSAcK']
        if metas is not None:
            for alk in metas:
                vals = temp_output_hits[temp_output_hits[wcvp_accepted_columns['name']] == taxa][
                    'Metabolite'].values
                self.assertIn(alk, vals)
