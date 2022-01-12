import os

import pandas as pd
from pkg_resources import resource_filename

from name_matching_cleaning import clean_ids, standardise_names_in_column

### Inputs
from powo_searches import search_powo

inputs_path = resource_filename(__name__, 'inputs')
input_species_csv = os.path.join(inputs_path, 'clean.csv')
littox1_csv = os.path.join(inputs_path, 'littox_matched_1.csv')
littox2_csv = os.path.join(inputs_path, 'littox_matched_2.csv')

### Temp outputs
temp_outputs_path = resource_filename(__name__, 'temp_outputs')
littox_temp_output_accepted_csv = os.path.join(temp_outputs_path, 'littox_accepted.csv')
powo_search_temp_output_csv = os.path.join(temp_outputs_path, 'powo_poisons.csv')
powo_search_temp_output_accepted_csv = os.path.join(temp_outputs_path, 'powo_poisons_accepted.csv')

### Outputs
output_path = resource_filename(__name__, 'outputs')
output_poison_csv = os.path.join(output_path, 'list_of_poisonous_plants.csv')


def prepare_littox_poisons() -> pd.DataFrame:
    col_name = "Poisonous"
    # Due to size of littox csv files, cannot use R script to match names
    # Used http://namematch.science.kew.org/csv
    # Get extended. Powo. Use header
    # Have two files to use one from 'Latin name provided' and one from 'latin namenoauthor'

    # First Save a copy as CSV (sheet - plant names)
    littox_db1 = pd.read_csv(littox1_csv, sep='\t')
    littox_db2 = pd.read_csv(littox2_csv, sep='\t')
    littox_db1['id'] = littox_db1['id'].apply(clean_ids)
    littox_db2['id'] = littox_db2['id'].apply(clean_ids)

    littox_db1 = littox_db1.dropna(subset=['id'])
    littox_db2 = littox_db2.dropna(subset=['id'])

    littox_db1 = littox_db1[littox_db1['Rank'] == 'SPECIES']
    littox_db2 = littox_db2[littox_db2['Rank'] == 'SPECIES']

    merged = pd.merge(littox_db1, littox_db2, how="inner")
    merged['Source'] = 'Littox'
    merged.rename(columns={'id': 'ID'}, inplace=True)
    merged.to_csv(littox_temp_output_accepted_csv)
    return merged


def get_powo_poisons():
    search_powo('poison,poisonous,toxic,deadly', powo_search_temp_output_csv)
    powo_poisons = pd.read_csv(powo_search_temp_output_csv)
    powo_poisons['fqId'] = powo_poisons['fqId'].apply(clean_ids)
    powo_poisons.rename(columns={'snippet': 'powo_snippet', 'fqId': 'ID', 'url': 'Source'}, inplace=True)
    powo_poisons['Source'] = 'POWO: ' + powo_poisons['Source'].astype(str)
    powo_poisons.to_csv(powo_search_temp_output_accepted_csv)


def compile_hits():
    powo_hits = pd.read_csv(powo_search_temp_output_accepted_csv)
    littox_hits = pd.read_csv(littox_temp_output_accepted_csv)

    all_dfs = [powo_hits, littox_hits]

    cols_to_keep = ['ID', 'family', 'name', 'rank', 'powo_snippet', 'ID', 'Source', "Source_x", "Source_y"]

    for df in all_dfs:
        cols_to_drop = [c for c in df.columns if
                        c not in cols_to_keep]
        df.drop(columns=cols_to_drop, inplace=True)

    all_poisons = pd.merge(powo_hits, littox_hits, on='ID')
    # Merge Sources:
    sources_cols = [c for c in all_poisons.columns.tolist() if 'Source' in c]
    for col in sources_cols:
        all_poisons[col] = all_poisons[col].astype('string')
        all_poisons[col] = all_poisons[col].fillna('')
    all_poisons['Sources'] = all_poisons[sources_cols].agg(':'.join, axis=1)
    all_poisons.drop(columns=sources_cols, inplace=True)

    all_poisons.to_csv(output_poison_csv)


def main():
    get_powo_poisons()
    prepare_littox_poisons()
    compile_hits()


if __name__ == '__main__':
    main()
