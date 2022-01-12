import os
import subprocess

import pandas as pd

from name_matching_cleaning import clean_ids

path_here = os.path.dirname(os.path.abspath(__file__))


def search_powo(search_terms: str, output_file: str):
    '''

    :param search_terms: string of terms e.g. 'poison,poisonous,toxic,deadly'
    :param output_file:
    :return:
    '''
    r_script = os.path.join(path_here, 'powo_search.R')
    command = f'Rscript "{r_script}" --out "{output_file}" --searchterms "{search_terms}"'

    subprocess.call(command, shell=True)


def clean_powo_output(powo_search_output_csv: str, output_csv: str):
    powo_poisons = pd.read_csv(powo_search_output_csv)
    powo_poisons['fqId'] = powo_poisons['fqId'].apply(clean_ids)
    powo_poisons.rename(
        columns={'snippet': 'powo_Snippet', 'name': 'Accepted_Name', 'fqId': 'Accepted_ID', 'url': 'Source',
                 'rank': 'Rank', 'family': 'Family'},
        inplace=True)
    powo_poisons['Source'] = 'POWO: ' + powo_poisons['Source'].astype(str)
    powo_poisons.to_csv(output_csv)
