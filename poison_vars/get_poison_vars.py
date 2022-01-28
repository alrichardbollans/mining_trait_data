import os

import pandas as pd
from pkg_resources import resource_filename

from name_matching_cleaning import clean_urn_ids, compile_hits
from powo_searches import search_powo

### Inputs


inputs_path = resource_filename(__name__, 'inputs')
input_species_csv = os.path.join(inputs_path, 'clean.csv')
littox1_csv = os.path.join(inputs_path, 'littox_matched_1.csv')
littox2_csv = os.path.join(inputs_path, 'littox_matched_2.csv')
useful_plants_file = os.path.join(inputs_path, 'useful_plant_processed_db.txt')

### Temp outputs
temp_outputs_path = resource_filename(__name__, 'temp_outputs')
littox_temp_output_accepted_csv = os.path.join(temp_outputs_path, 'littox_accepted.csv')
useful_temp_output_accepted_csv = os.path.join(temp_outputs_path, 'useful_accepted.csv')
powo_search_temp_output_accepted_csv = os.path.join(temp_outputs_path, 'powo_poisons_accepted.csv')

### Outputs
output_path = resource_filename(__name__, 'outputs')
output_poison_csv = os.path.join(output_path, 'list_of_poisonous_plants.csv')


def prepare_useful_plants_poisons() -> pd.DataFrame:
    useful_db = pd.read_csv(useful_plants_file, encoding='latin_1', sep='\t')

    useful_db = useful_db[useful_db['Poisons'] == 1]

    useful_db.rename(
        columns={'acc_ipniid': 'Accepted_ID', 'binomial_acc_name': 'Accepted_Name'},
        inplace=True)
    useful_db['Accepted_Rank'] = 'Species'
    useful_db['Accepted_Species'] = useful_db['Accepted_Name']

    useful_db.dropna(subset=['Accepted_ID'], inplace=True)

    # Drop columns containing 'Source' as this gets confused when compiling all data
    cs = [c for c in useful_db.columns if 'Source' in c]
    useful_db.drop(columns=cs, inplace=True)
    # Then add a source column
    useful_db['Source'] = 'Useful Plants Data'

    useful_db.to_csv(useful_temp_output_accepted_csv)
    return useful_db


def prepare_littox_poisons() -> pd.DataFrame:
    # Due to size of littox csv files, cannot use R script to match names
    # Used http://namematch.science.kew.org/csv
    # Get extended. Powo. Use header
    # Have two files to use one from 'Latin name provided' and one from 'latin namenoauthor'

    # First Save a copy as CSV (sheet - plant names)
    littox_db1 = pd.read_csv(littox1_csv, sep='\t')
    littox_db2 = pd.read_csv(littox2_csv, sep='\t')
    littox_db1['id'] = littox_db1['id'].apply(clean_urn_ids)
    littox_db2['id'] = littox_db2['id'].apply(clean_urn_ids)

    littox_db1 = littox_db1.dropna(subset=['id'])
    littox_db2 = littox_db2.dropna(subset=['id'])

    merged = pd.merge(littox_db1, littox_db2, how="inner")
    merged['Source'] = 'Littox'
    # Note these IDs aren't actually accepted
    merged.rename(columns={'id': 'Accepted_ID', 'Scientific Name': 'Accepted_Name'}, inplace=True)
    merged.to_csv(littox_temp_output_accepted_csv)
    return merged


def get_powo_poisons():
    search_powo(['poison', 'poisonous', 'toxic', 'deadly'],
                powo_search_temp_output_accepted_csv,
                families_of_interest=['Rubiaceae', 'Apocynaceae'],
                filters=['species', 'infraspecies']
                )


def main():
    get_powo_poisons()
    prepare_littox_poisons()
    prepare_useful_plants_poisons()
    powo_hits = pd.read_csv(powo_search_temp_output_accepted_csv)
    littox_hits = pd.read_csv(littox_temp_output_accepted_csv)
    useful_hits = pd.read_csv(useful_temp_output_accepted_csv)
    compile_hits([useful_hits, powo_hits, littox_hits], output_poison_csv)


if __name__ == '__main__':
    main()
