import os

import numpy as np
import pandas as pd
from pkg_resources import resource_filename

### Inputs
from pykew import powo_terms

from name_matching_cleaning import get_accepted_info_from_names_in_column, generate_temp_output_file_paths, COL_NAMES, \
    merge_on_accepted_id, compile_hits
from powo_searches import search_powo

inputs_path = resource_filename(__name__, 'inputs')
morph_input_csv = os.path.join(inputs_path, '18455.txt')
emergence_input_csv = os.path.join(inputs_path, 'emergence_data.csv')
latex_input_csv = os.path.join(inputs_path, 'latex_data.csv')
corolla_input_csv = os.path.join(inputs_path, 'corolla_data.csv')
### Temp outputs

temp_outputs_path = resource_filename(__name__, 'temp_outputs')

spine_temp_output_cleaned_csv, spine_temp_output_accepted_csv = generate_temp_output_file_paths(
    'spines_try', temp_outputs_path)
hair_temp_output_cleaned_csv, hair_temp_output_accepted_csv = generate_temp_output_file_paths(
    'hairs_try', temp_outputs_path)

spine_powo_search_temp_output_cleaned_csv, spine_powo_search_temp_output_accepted_csv = generate_temp_output_file_paths(
    'spines_powo', temp_outputs_path)

hairs_powo_search_temp_output_cleaned_csv, hairs_powo_search_temp_output_accepted_csv = generate_temp_output_file_paths(
    'hairs_powo', temp_outputs_path)

### Outputs
output_path = resource_filename(__name__, 'outputs')
spines_output_csv = os.path.join(output_path, 'spines_hits.csv')
hairy_output_csv = os.path.join(output_path, 'hairy_hits.csv')

#
# Values for each spine feature which don't indicate spines
spine_values_to_drop = {'Thorn / spine length': [str(0), 0],
                        'Spinescence / thorniness': ['spines absent', str(0), 0, 'no', 'Absence'],
                        'Thorn density': [str(0), 0],
                        'Leaf spines: upper': ['no'],
                        'Leaf Spines: lower': ['no'],
                        'Leaf Spines: midrib/veins': ['no'],
                        'Leaf Spines: marginal': ['no'],
                        'Leaf Spines: terminal': ['no'],
                        'Leaf thorn': ['no'],
                        'Stem spiny': ['no'],
                        'Stem thorny': ['no'],
                        'Other spines/thorns': ['no'],
                        'Leaf spines': ['no'],
                        'Thorns elsewhere': ['no']
                        }
# Values for each hair feature which doesn't indicate hairs
hair_values_to_drop = {'Leaf trichome canopy height': [],
                       'Pubescence: presence and abundance of water-absorbing hairs on leaves (e.g., Bromeliaceae)': [1,
                                                                                                                      str(1)],
                       'Pubescence (cottony + - horizontal indumentum)': [1, str(1)],
                       'Hairs orientation': [],
                       'Pruinose: above': ['no'],
                       'Pruinose: below': ['no'],
                       'Pruinose: midrib/veins': ['no'],
                       'Pruinose: petiole': ['no'],
                       'Leaf pruinose': ['no'],
                       'Leaf hair length': [0, str(0)],
                       'Leaf hairiness': ['no hairs', 'slightly hairy (few hairs or hairs only along veins)',
                                          'only as young plant with hairs, old no hairs', 'no'],
                       'Stem hair length': [0, str(0)],
                       'Pubescence (ascending hairs or papillae)': [1, str(1)],
                       'Leaf: trichome density': [],
                       'Leaf hairiness: top': ['no', 'no hairs', 'only as young plant with hairs', 'other'],
                       'Leaf hairiness: bottom': ['no', 'no hairs', 'only as young plant with hairs', 'other'],
                       'Lair hairiness: midrib/veins': ['no'],
                       'Leaf hairiness: marginal': ['no'],
                       'Leaf with basal hairs': ['no'],
                       'Leaf pubescent: top': ['no'],
                       'Leaf pubescent: bottom': ['no'],
                       'Leaf pubescent: marginal': ['no'],
                       'Leaf pubescent: midrib/veins': ['no'],
                       'Stem hairy': ['no'],
                       'Stem pubescent': ['no'],
                       'Leaf pubescence': ['no']

                       }


def clean_try_db():
    cols_to_drop = ['LastName', 'FirstName']
    morph_data = pd.read_csv(morph_input_csv, encoding='latin_1', sep='\t')
    morph_data.dropna(subset=['TraitName'], inplace=True)

    morph_data.drop(columns=cols_to_drop, inplace=True)

    emergence_db = morph_data[morph_data['TraitName'].str.contains('emergence')]
    latex_db = morph_data[morph_data['TraitName'].str.contains('latex')]
    corolla_db = morph_data[morph_data['TraitName'].str.contains('corolla')]

    emergence_db = emergence_db.dropna(axis=1, how='all')
    latex_db = latex_db.dropna(axis=1, how='all')
    corolla_db = corolla_db.dropna(axis=1, how='all')

    emergence_db.to_csv(emergence_input_csv)
    latex_db.to_csv(latex_input_csv)
    corolla_db.to_csv(corolla_input_csv)

    # Check
    x = len(emergence_db.index) + len(latex_db.index) + len(corolla_db.index)
    if x != len(morph_data.index):
        raise ValueError('Some items have been lost')


def get_accepted_info_hair_hits():
    emergence_db = pd.read_csv(emergence_input_csv)
    emergence_db.dropna(subset=['OrigValueStr'], inplace=True)

    # First remove undesired traits (in this case hair)
    hair_db = emergence_db[~emergence_db['DataName'].isin(spine_values_to_drop.keys())]
    # Remove unpub works as can't check the meanings of values.
    hair_db = hair_db[hair_db['Reference'] != 'unpub.']

    # Look at possible values
    for c in hair_db['DataName'].unique():
        specific_trait = hair_db[hair_db['DataName'] == c]

        print(c)
        print(list(specific_trait['OrigValueStr'].unique()))

    for k in hair_values_to_drop:
        hair_db = hair_db[
            ~((hair_db['DataName'] == k) & (hair_db['OrigValueStr'].isin(hair_values_to_drop[k])))]

    for i in hair_db['DataName'].unique():
        if i not in hair_values_to_drop.keys():
            raise ValueError(f'Unknown hair dataname: {i}')

    for y in ['thorn', 'spiny', 'spine']:
        if any(y in x for x in list(hair_db['DataName'].unique())):
            raise ValueError(f'{y} found in Dataname column')

    hair_db.to_csv(hair_temp_output_cleaned_csv)
    get_accepted_info_from_names_in_column('AccSpeciesName', hair_temp_output_cleaned_csv,
                                           hair_temp_output_accepted_csv)


def get_accepted_info_spine_hits():
    emergence_db = pd.read_csv(emergence_input_csv)
    emergence_db.dropna(subset=['OrigValueStr'], inplace=True)

    # First remove undesired traits (in this case hair)
    spine_db = emergence_db[~emergence_db['DataName'].isin(hair_values_to_drop.keys())]
    # Remove unpub works as can't check the meanings of values.
    spine_db = spine_db[spine_db['Reference'] != 'unpub.']

    # Look at possible values
    for c in spine_db['DataName'].unique():
        specific_trait = spine_db[spine_db['DataName'] == c]

        print(c)
        print(specific_trait['OrigValueStr'].unique())

    for k in spine_values_to_drop:
        spine_db = spine_db[
            ~((spine_db['DataName'] == k) & (spine_db['OrigValueStr'].isin(spine_values_to_drop[k])))]

    for i in spine_db['DataName'].unique():
        if i not in spine_values_to_drop.keys():
            raise ValueError(f'Unknown spine dataname: {i}')

    for y in ['hair', 'pubescence', 'trichome']:
        if any(y in x for x in list(spine_db['DataName'].unique())):
            raise ValueError(f'{y} found in Dataname column')

    spine_db.to_csv(spine_temp_output_cleaned_csv)
    get_accepted_info_from_names_in_column('AccSpeciesName', spine_temp_output_cleaned_csv,
                                           spine_temp_output_accepted_csv)


def clean_accepted_try_hits(temp_output_accepted_csv: str):
    df = pd.read_csv(temp_output_accepted_csv)

    df['OrigUnitStr'].fillna('', inplace=True)
    df['try_Snippet'] = df['DataName'] + ':' + df['OrigValueStr'] + df[
        'OrigUnitStr']
    df[COL_NAMES['single_source']] = 'TRY (' + df['Reference'] + ')'

    df.to_csv(temp_output_accepted_csv)


def get_powo_spine_hits():
    search_powo(['spine', 'thorn', 'spike'], spine_powo_search_temp_output_cleaned_csv,
                spine_powo_search_temp_output_accepted_csv,
                characteristics_to_search=['leaf', 'inflorescence', 'appearance', 'fruit'],
                families_of_interest=['Rubiaceae', 'Apocynaceae'], filters=['genera','species','infraspecies'])


def get_powo_hair_hits():
    search_powo(['hairs', 'hairy'], hairs_powo_search_temp_output_cleaned_csv,
                hairs_powo_search_temp_output_accepted_csv,
                characteristics_to_search=['leaf', 'inflorescence', 'appearance'],
                families_of_interest=['Rubiaceae', 'Apocynaceae'], filters=['genera','species','infraspecies'])


def main():
    clean_try_db()
    get_accepted_info_spine_hits()
    clean_accepted_try_hits(spine_temp_output_accepted_csv)

    get_powo_spine_hits()

    powo_spine_hits = pd.read_csv(spine_powo_search_temp_output_accepted_csv)
    try_spine_hits = pd.read_csv(spine_temp_output_accepted_csv)

    all_spine_dfs = [try_spine_hits, powo_spine_hits]
    compile_hits(all_spine_dfs, spines_output_csv)

    get_accepted_info_hair_hits()
    clean_accepted_try_hits(hair_temp_output_accepted_csv)

    get_powo_hair_hits()

    powo_hair_hits = pd.read_csv(hairs_powo_search_temp_output_accepted_csv)
    try_hair_hits = pd.read_csv(hair_temp_output_accepted_csv)

    all_hair_hits = [powo_hair_hits, try_hair_hits]
    compile_hits(all_hair_hits, hairy_output_csv)


if __name__ == '__main__':
    main()
