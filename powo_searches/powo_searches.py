import os
import subprocess

import pandas as pd

from name_matching_cleaning import col_names, standardise_names_in_column, filter_out_ranks

path_here = os.path.dirname(os.path.abspath(__file__))


def search_powo(search_terms: str, temp_output_file: str, accepted_output_file: str):
    # Would be better to search for all and then find accepted names
    '''

    :param accepted_output_file:
    :param temp_output_file:
    :param search_terms: string of terms e.g. 'poison,poisonous,toxic,deadly'
    :return:
    '''
    r_script = os.path.join(path_here, 'powo_search.R')
    command = f'Rscript "{r_script}" --out "{temp_output_file}" --searchterms "{search_terms}"'

    subprocess.call(command, shell=True)

    powo_poisons = pd.read_csv(temp_output_file)
    powo_poisons.rename(
        columns={'snippet': 'powo_Snippet',
                 'url': col_names['single_source'], 'family': 'Family'},
        inplace=True)
    powo_poisons['Source'] = 'POWO pages(' + powo_poisons['Source'].astype(str) + ')'

    powo_poisons.to_csv(temp_output_file)
    standardise_names_in_column('name', temp_output_file, accepted_output_file)
