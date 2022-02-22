import os

import pandas as pd
from pkg_resources import resource_filename

import wikipedia_searches
from cleaning import compile_hits
from automatchnames import clean_urn_ids, get_accepted_info_from_names_in_column
from powo_searches import search_powo

### Inputs


_inputs_path = resource_filename(__name__, 'inputs')
_input_species_csv = os.path.join(_inputs_path, 'clean.csv')

_useful_plants_file = os.path.join(_inputs_path, 'useful_plant_processed_db.txt')
_cornell_file = os.path.join(_inputs_path, 'Plants Poisonous to Livestock Cornell University.html')
_CPCS_file = os.path.join(_inputs_path, 'California Poison Control System (CPCS).html')
_UCANR_toxic_file = os.path.join(_inputs_path, 'UCANR_toxic.html')
_UCANR_nontoxic_file = os.path.join(_inputs_path, 'UCANR_nontoxic.html')

### Temp outputs
_temp_outputs_path = resource_filename(__name__, 'temp_outputs')
_littox_temp_output_accepted_csv = os.path.join(_temp_outputs_path, 'littox_accepted.csv')
_useful_temp_output_accepted_csv = os.path.join(_temp_outputs_path, 'useful_accepted.csv')
_powo_search_temp_output_accepted_csv = os.path.join(_temp_outputs_path, 'powo_poisons_accepted.csv')
_wiki_search_temp_output_csv = os.path.join(_temp_outputs_path, 'wiki_poisons.csv')
_wiki_search_temp_output_accepted_csv = os.path.join(_temp_outputs_path, 'wiki_poisons_accepted.csv')
_cornell_temp_accepted_csv = os.path.join(_temp_outputs_path, 'cornell_accepted.csv')
_CPCS_toxic_temp_accepted_csv = os.path.join(_temp_outputs_path, 'CPCS_toxic_accepted.csv')
_CPCS_nontoxic_temp_accepted_csv = os.path.join(_temp_outputs_path, 'CPCS_nontoxic_accepted.csv')
_UCANR_toxic_temp_accepted_csv = os.path.join(_temp_outputs_path, 'UCANR_toxic_accepted.csv')
_UCANR_nontoxic_temp_accepted_csv = os.path.join(_temp_outputs_path, 'UCANR_nontoxic_accepted.csv')
### Outputs
_output_path = resource_filename(__name__, 'outputs')
output_poison_csv = os.path.join(_output_path, 'list_of_poisonous_plants.csv')
output_nonpoison_csv = os.path.join(_output_path, 'list_of_nonpoisonous_plants.csv')


def prepare_cornell_data() -> pd.DataFrame:
    tables = pd.read_html(_cornell_file)
    tables[0]['Source'] = 'Cornell CALS'
    db_acc = get_accepted_info_from_names_in_column(tables[0], 'Scientific Name')
    db_acc.to_csv(_cornell_temp_accepted_csv)
    return db_acc


def prepare_CPCS_data():
    tables = pd.read_html(_CPCS_file)

    non_toxic_db = tables[1]
    # Remove letter headers
    non_toxic_db = non_toxic_db[~non_toxic_db['Latin or scientific name'].str.contains('^[A-Z]$', regex=True)]
    acc_non_toxic = get_accepted_info_from_names_in_column(non_toxic_db, 'Latin or scientific name')
    acc_non_toxic['Source'] = 'CPCS'
    acc_non_toxic.to_csv(_CPCS_nontoxic_temp_accepted_csv)

    toxic_db = tables[4]
    toxic_db = toxic_db[~toxic_db['Latin or scientific name'].str.contains('^[A-Z]$', regex=True)]
    acc_toxic = get_accepted_info_from_names_in_column(toxic_db, 'Latin or scientific name')
    acc_toxic['Source'] = 'CPCS'
    acc_toxic.to_csv(_CPCS_toxic_temp_accepted_csv)


def prepare_toxic_UCANR_data():
    toxic_tables = pd.read_html(_UCANR_toxic_file,header=0)

    toxic_db = toxic_tables[0]
    acc_toxic = get_accepted_info_from_names_in_column(toxic_db, 'Toxic plants: Scientific name')
    acc_toxic['Source'] = 'UCANR'
    acc_toxic.to_csv(_UCANR_toxic_temp_accepted_csv)

def prepare_nontoxic_UCANR_data():
    nontoxic_tables = pd.read_html(_UCANR_nontoxic_file,header=0)

    nontoxic_db = nontoxic_tables[0]
    acc_nontoxic = get_accepted_info_from_names_in_column(nontoxic_db, 'Safe plants: Scientific name')
    acc_nontoxic['Source'] = 'UCANR'
    acc_nontoxic.to_csv(_UCANR_nontoxic_temp_accepted_csv)

def prepare_useful_plants_poisons() -> pd.DataFrame:
    useful_db = pd.read_csv(_useful_plants_file, encoding='latin_1', sep='\t')

    useful_db = useful_db[useful_db['Poisons'] == 1]

    useful_db.rename(
        columns={'acc_ipniid': 'Accepted_ID', 'binomial_acc_name': 'Accepted_Name'},
        inplace=True)
    useful_db['Accepted_Rank'] = 'Species'
    useful_db['Accepted_Species'] = useful_db['Accepted_Name']
    useful_db['Accepted_Species_ID'] = useful_db['Accepted_ID']

    useful_db.dropna(subset=['Accepted_ID'], inplace=True)

    # Drop columns containing 'Source' as this gets confused when compiling all data
    cs = [c for c in useful_db.columns if 'Source' in c]
    useful_db.drop(columns=cs, inplace=True)
    # Then add a source column
    useful_db['Source'] = 'Useful Plants Data'

    useful_db.to_csv(_useful_temp_output_accepted_csv)
    return useful_db


def prepare_littox_poisons() -> pd.DataFrame:
    littox_db = pd.read_csv(os.path.join(_inputs_path, 'Littox_210428_copy.csv'))
    littox_db['Source'] = 'LITTOX'
    littox_db_acc = get_accepted_info_from_names_in_column(littox_db, 'Latin name provided')
    littox_db_acc.to_csv(_littox_temp_output_accepted_csv)
    return littox_db_acc


def get_powo_poisons():
    search_powo(['poison', 'poisonous', 'toxic', 'deadly'],
                _powo_search_temp_output_accepted_csv,
                families_of_interest=['Rubiaceae', 'Apocynaceae'],
                filters=['species', 'infraspecies']
                )


def get_wiki_poisons():
    wiki_df = wikipedia_searches.search_for_poisons(_wiki_search_temp_output_csv)
    acc_wiki_df = get_accepted_info_from_names_in_column(wiki_df, 'name')
    acc_wiki_df.to_csv(_wiki_search_temp_output_accepted_csv)

    return acc_wiki_df


def get_nonpoison_hits():
    if not os.path.isdir(_temp_outputs_path):
        os.mkdir(_temp_outputs_path)
    if not os.path.isdir(_output_path):
        os.mkdir(_output_path)

    prepare_CPCS_data()
    prepare_nontoxic_UCANR_data()
    ucanr_hits = pd.read_csv(_UCANR_nontoxic_temp_accepted_csv)
    CPCS_hits = pd.read_csv(_CPCS_nontoxic_temp_accepted_csv)

    compile_hits([CPCS_hits, ucanr_hits], output_nonpoison_csv)


def get_poison_hits():
    if not os.path.isdir(_temp_outputs_path):
        os.mkdir(_temp_outputs_path)
    if not os.path.isdir(_output_path):
        os.mkdir(_output_path)

    get_wiki_poisons()
    get_powo_poisons()
    prepare_littox_poisons()
    prepare_useful_plants_poisons()

    prepare_cornell_data()
    prepare_CPCS_data()
    prepare_toxic_UCANR_data()
    ucanr_hits = pd.read_csv(_UCANR_toxic_temp_accepted_csv)
    CPCS_hits = pd.read_csv(_CPCS_toxic_temp_accepted_csv)
    cornell_hits = pd.read_csv(_cornell_temp_accepted_csv)
    wiki_hits = pd.read_csv(_wiki_search_temp_output_accepted_csv)
    powo_hits = pd.read_csv(_powo_search_temp_output_accepted_csv)
    littox_hits = pd.read_csv(_littox_temp_output_accepted_csv)
    littox_hits['Source'] = 'LITTOX'
    useful_hits = pd.read_csv(_useful_temp_output_accepted_csv)
    useful_hits['Accepted_Species_ID'] = useful_hits['Accepted_ID']
    compile_hits([useful_hits, powo_hits, littox_hits, wiki_hits, cornell_hits, CPCS_hits, ucanr_hits],
                 output_poison_csv)


if __name__ == '__main__':
    get_poison_hits()
    get_nonpoison_hits()
