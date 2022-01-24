import os

import numpy as np
import pandas as pd
from pkg_resources import resource_filename

### Inputs
from name_matching_cleaning import standardise_names_in_column, generate_temp_output_file_paths, COL_NAMES, \
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

spine_powo_search_temp_output_cleaned_csv, spine_powo_search_temp_output_accepted_csv = generate_temp_output_file_paths(
    'spines_powo', temp_outputs_path)

### Outputs
output_path = resource_filename(__name__, 'outputs')
spines_output_csv = os.path.join(output_path, 'spines_hits.csv')


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


def get_accepted_info_spine_hits():
    emergence_db = pd.read_csv(emergence_input_csv)
    emergence_db.dropna(subset=['OrigValueStr'], inplace=True)
    # Look at possible values
    for c in emergence_db['DataName'].unique():
        specific_trait = emergence_db[emergence_db['DataName'] == c]

        print(c)
        print(specific_trait['OrigValueStr'].unique())

    trs_to_drop = ['Leaf trichome canopy height',
                   'Pubescence: presence and abundance of water-absorbing hairs on leaves (e.g., Bromeliaceae)',
                   'Pubescence (cottony + - horizontal indumentum)', 'Hairs orientation', 'Pruinose: above',
                   'Pruinose: below', 'Pruinose: midrib/veins', 'Pruinose: petiole', 'Leaf pruinose',
                   'Leaf hair length',
                   'Leaf hairiness', 'Stem hair length', 'Pubescence (ascending hairs or papillae)',
                   'Leaf: trichome density',
                   'Leaf hairiness: top',
                   'Leaf hairiness: bottom',
                   'Lair hairiness: midrib/veins',
                   'Leaf hairiness: marginal',
                   'Leaf with basal hairs',
                   'Leaf pubescent: top',
                   'Leaf pubescent: bottom',
                   'Leaf pubescent: marginal',
                   'Leaf pubescent: midrib/veins',
                   'Stem hairy',
                   'Stem pubescent',
                   'Leaf pubescence'

                   ]

    # Values for each feature which don't indicate spines
    val_to_drop = {'Thorn / spine length': [str(0), 0],
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
    # First remove undesired traits (in this case hair)
    spine_db = emergence_db[~emergence_db['DataName'].isin(trs_to_drop)]
    # Remove unpub works as can't check the meanings of values.
    spine_db = spine_db[spine_db['Reference'] != 'unpub.']

    for k in val_to_drop:
        spine_db = spine_db[
            ~((spine_db['DataName'] == k) & (spine_db['OrigValueStr'].isin(val_to_drop[k])))]

    spine_db.to_csv(spine_temp_output_cleaned_csv)
    standardise_names_in_column('AccSpeciesName', spine_temp_output_cleaned_csv, spine_temp_output_accepted_csv)

def clean_accepted_spine_hits():
    spine_db = pd.read_csv(spine_temp_output_accepted_csv)
    spine_db['OrigUnitStr'].fillna('',inplace=True)
    spine_db['try_Snippet'] = spine_db['DataName'] + ':' + spine_db['OrigValueStr'] + spine_db[
        'OrigUnitStr']
    spine_db[COL_NAMES['single_source']] = 'TRY (' + spine_db['Reference'] + ')'


    for y in ['hair', 'pubescence', 'trichome']:
        if any(y in x for x in list(spine_db['DataName'].unique())):
            raise ValueError(f'{y} found in Dataname column')

    spine_db.to_csv(spine_temp_output_accepted_csv)

def get_powo_spine_hits():
    search_powo('spine,thorn,spike', spine_powo_search_temp_output_cleaned_csv,
                spine_powo_search_temp_output_accepted_csv)


def main():
    # clean_try_db()
    # get_accepted_info_spine_hits()
    clean_accepted_spine_hits()
    # get_powo_spine_hits()

    powo_hits = pd.read_csv(spine_powo_search_temp_output_accepted_csv)
    try_hits = pd.read_csv(spine_temp_output_accepted_csv)

    all_dfs = [try_hits, powo_hits]
    compile_hits(all_dfs, spines_output_csv)


if __name__ == '__main__':
    main()
