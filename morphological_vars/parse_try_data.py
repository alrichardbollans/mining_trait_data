import os

import pandas as pd
from pkg_resources import resource_filename
from typing import List

from name_matching_cleaning import get_accepted_info_from_names_in_column, COL_NAMES

inputs_path = resource_filename(__name__, 'inputs')
_try_morph_input_csv = os.path.join(inputs_path, '18455.txt')
_try_emergence_input_csv = os.path.join(inputs_path, 'emergence_data.csv')
_try_latex_input_csv = os.path.join(inputs_path, 'latex_data.csv')
_try_corolla_input_csv = os.path.join(inputs_path, 'corolla_data.csv')

### Temp outputs

temp_outputs_path = resource_filename(__name__, 'temp_outputs')

try_spine_temp_output_accepted_csv = os.path.join(temp_outputs_path, 'spines_try' + '_accepted.csv')
try_no_spine_temp_output_accepted_csv = os.path.join(temp_outputs_path, 'no_spines_try' + '_accepted.csv')
try_hair_temp_output_accepted_csv = os.path.join(temp_outputs_path, 'hairs_try' + '_accepted.csv')

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
    morph_data = pd.read_csv(_try_morph_input_csv, encoding='latin_1', sep='\t')
    morph_data = morph_data.dropna(subset=['TraitName'])

    morph_data = morph_data.drop(columns=cols_to_drop)

    emergence_db = morph_data[morph_data['TraitName'].str.contains('emergence')]
    latex_db = morph_data[morph_data['TraitName'].str.contains('latex')]
    corolla_db = morph_data[morph_data['TraitName'].str.contains('corolla')]

    emergence_db = emergence_db.dropna(axis=1, how='all')
    latex_db = latex_db.dropna(axis=1, how='all')
    corolla_db = corolla_db.dropna(axis=1, how='all')

    emergence_db.to_csv(_try_emergence_input_csv)
    latex_db.to_csv(_try_latex_input_csv)
    corolla_db.to_csv(_try_corolla_input_csv)

    # Check
    x = len(emergence_db.index) + len(latex_db.index) + len(corolla_db.index)
    if x != len(morph_data.index):
        raise ValueError('Some items have been lost')


def get_accepted_info_try_hair_hits():
    emergence_db = pd.read_csv(_try_emergence_input_csv)
    emergence_db = emergence_db.dropna(subset=['OrigValueStr'])

    hair_db = clean_try_hits(emergence_db, list(spine_values_to_drop.keys()))

    for k in hair_values_to_drop:
        hair_db = hair_db[
            ~((hair_db['DataName'] == k) & (hair_db['OrigValueStr'].isin(hair_values_to_drop[k])))]

    for i in hair_db['DataName'].unique():
        if i not in hair_values_to_drop.keys():
            raise ValueError(f'Unknown hair dataname: {i}')

    for y in ['thorn', 'spiny', 'spine']:
        if any(y in x for x in list(hair_db['DataName'].unique())):
            raise ValueError(f'{y} found in Dataname column')

    hair_try_acc = get_accepted_info_from_names_in_column(hair_db, 'AccSpeciesName')
    hair_try_acc.to_csv(try_hair_temp_output_accepted_csv)


def get_accepted_try_info_spine_hits():
    emergence_db = pd.read_csv(_try_emergence_input_csv)
    emergence_db = emergence_db.dropna(subset=['OrigValueStr'])
    spine_hits_db = clean_try_hits(emergence_db, list(hair_values_to_drop.keys()))
    spine_no_hits = spine_hits_db.copy(deep=True)

    for k in spine_values_to_drop:
        spine_hits_db = spine_hits_db[
            ~((spine_hits_db['DataName'] == k) & (spine_hits_db['OrigValueStr'].isin(spine_values_to_drop[k])))]

    no_hit_mask = ' | '.join(
        [f'((spine_no_hits["DataName"] == "{k}") & (spine_no_hits["OrigValueStr"].isin(spine_values_to_drop["{k}"])))'
         for k
         in spine_values_to_drop])

    spine_no_hits = spine_no_hits[eval(no_hit_mask)]

    for i in spine_hits_db['DataName'].unique():
        if i not in spine_values_to_drop.keys():
            raise ValueError(f'Unknown spine dataname: {i}')

    for y in ['hair', 'pubescence', 'trichome']:
        if any(y in x for x in list(spine_hits_db['DataName'].unique())):
            raise ValueError(f'{y} found in Dataname column')
        if any(y in x for x in list(spine_no_hits['DataName'].unique())):
            raise ValueError(f'{y} found in Dataname column')

    spine_try_acc = get_accepted_info_from_names_in_column(spine_hits_db, 'AccSpeciesName')
    spine_try_acc.to_csv(try_spine_temp_output_accepted_csv)

    no_spine_try_acc = get_accepted_info_from_names_in_column(spine_no_hits, 'AccSpeciesName')
    no_spine_try_acc.to_csv(try_no_spine_temp_output_accepted_csv)


def clean_try_hits(df: pd.DataFrame, traits_to_drop: List[str]) -> pd.DataFrame:
    # First remove undesired traits
    df = df[~df['DataName'].isin(traits_to_drop)]

    # Look at possible values
    for c in df['DataName'].unique():
        specific_trait = df[df['DataName'] == c]

        print(c)
        print(specific_trait['OrigValueStr'].unique())

    # Remove unpub works as can't check the meanings of values.
    df = df[df['Reference'] != 'unpub.']
    df['OrigUnitStr'].fillna('', inplace=True)
    df['try_Snippet'] = df['DataName'] + ':' + df['OrigValueStr'] + df[
        'OrigUnitStr']
    df[COL_NAMES['single_source']] = 'TRY (' + df['Reference'] + ')'

    return df


def main():
    clean_try_db()
    get_accepted_info_try_hair_hits()
    get_accepted_try_info_spine_hits()


if __name__ == '__main__':
    main()
