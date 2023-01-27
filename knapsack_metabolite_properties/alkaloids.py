from typing import Union

import pandas as pd

from knapsack_searches import kn_formula_column, kn_metabolite_name_column
from knapsack_metabolite_properties import get_alkaloids_from_kegg_brite


def is_alkaloid(name: str, formula: str) -> Union[list[Union[bool, str]], str]:
    '''
    Returns true if alkaloid
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
            if "n" in formula.lower():
                return 'N_and_ends_in_ine'

    return 'False'


def get_alkaloids_from_metabolites(metabolites_table: pd.DataFrame, temp_output_csv: str = None,
                                   output_csv: str = None) -> pd.DataFrame:
    '''

    :param metabolites_table: from get_metabolites_in_family
    :param temp_output_csv:
    :param output_csv:
    :return:
    '''
    df_copy = metabolites_table.copy(deep=True)
    df_copy['is_alkaloid'] = df_copy.apply(
        lambda x: is_alkaloid(x[kn_metabolite_name_column], x[kn_formula_column]), axis=1)

    if temp_output_csv is not None:
        df_copy.to_csv(temp_output_csv)

    df_copy = df_copy[df_copy['is_alkaloid'] != 'False']
    if output_csv is not None:
        df_copy.to_csv(output_csv)

    return df_copy
