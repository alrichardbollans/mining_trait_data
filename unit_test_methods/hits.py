import unittest

import pandas as pd
from wcvp_download import wcvp_accepted_columns

from data_compilation_methods import compiled_sources_col


class confirming_hits(unittest.TestCase):
    def confirm_hit(self, taxa: str, output_hits: pd.DataFrame):
        
        self.assertIn(taxa, output_hits[wcvp_accepted_columns['name']].values.tolist())

    def confirm_no_hit(self, taxa: str, output_hits: pd.DataFrame):
        
        self.assertNotIn(taxa, output_hits[wcvp_accepted_columns['name']].values.tolist())

    def confirm_powo_hit(self, taxa: str, output_hits: pd.DataFrame):
        
        self.assertIn('POWO', output_hits[output_hits[wcvp_accepted_columns['name']] == taxa][compiled_sources_col].values[0])

    def confirm_knapsack_hit(self, taxa: str, output_hits: pd.DataFrame, alkaloids=None):

        self.assertIn('KNApSAcK', output_hits[output_hits[wcvp_accepted_columns['name']] == taxa][compiled_sources_col].values[0])

        if alkaloids is not None:
            for alk in alkaloids:
                self.assertIn(alk, output_hits[output_hits[wcvp_accepted_columns['name']] == taxa]['knapsack_snippet'].values[0])
