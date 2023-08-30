import re
from typing import List

import pandas as pd

from knapsack_searches import kn_formula_column
from metabolite_properties import get_alkaloids_from_kegg_brite


def is_alkaloid_from_name_and_formulae(name: str, formulae: List[str]) -> str:
    '''
    Returns true if known alkaloid or if name ends in 'ine' and formula contains 'N'
    :param name:
    :param formula:
    :return:
    '''
    lower_name = name.lower()
    stripped_name = lower_name.strip()
    alkaloids_not_ending_in_ine = ['Kopsanone', 'Palicoside', 'Strictosidinic acid']
    known_non_alkaloids = []
    manual_known_alkaloids = []
    known_alkaloids = get_alkaloids_from_kegg_brite() + alkaloids_not_ending_in_ine + manual_known_alkaloids
    suffixes = ["ine-", "ine ", "ine+", "ine("]
    if any(alk.lower() in stripped_name.split() for alk in known_alkaloids):
        return 'in_known_alkaloids'
    elif any(stripped_name in alk.lower().split() for alk in known_alkaloids):
        return 'in_known_alkaloids'
    elif stripped_name not in known_non_alkaloids:
        if any(s.lower() in stripped_name for s in suffixes) or stripped_name.endswith('ine'):
            for formula in formulae:
                if formula == formula:
                    if "n" in formula.lower():
                        return 'N_and_ends_in_ine'

    return 'False'


def get_alkaloids_from_metabolites(metabolites_table: pd.DataFrame, metabolite_name_col: str, temp_output_csv: str = None,
                                   output_csv: str = None) -> pd.DataFrame:
    '''

    :param metabolites_table: from get_metabolites_in_family
    :param temp_output_csv:
    :param output_csv:
    :return:
    '''
    df_copy = metabolites_table.copy(deep=True)
    df_copy['is_alkaloid_from_name_and_formula'] = df_copy.apply(
        lambda x: is_alkaloid_from_name_and_formulae(x[metabolite_name_col], [x[kn_formula_column], x['SMILES']]), axis=1)

    if temp_output_csv is not None:
        df_copy.to_csv(temp_output_csv)

    df_copy = df_copy[df_copy['is_alkaloid_from_name_and_formula'] != 'False']
    if output_csv is not None:
        df_copy.to_csv(output_csv)

    return df_copy


def get_N_containing_from_metabolites(metabolites_table: pd.DataFrame, output_csv: str = None) -> pd.DataFrame:
    '''

    :param metabolites_table: from get_metabolites_in_family
    :param output_csv:
    :return:
    '''

    p = re.compile(r'n', flags=re.IGNORECASE)
    n_containing_df = metabolites_table[
        metabolites_table[kn_formula_column].str.contains(p, na=False) | metabolites_table['SMILES'].str.contains(p, na=False)]

    if output_csv is not None:
        n_containing_df.to_csv(output_csv)

    return n_containing_df
