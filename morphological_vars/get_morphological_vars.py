import os

import pandas as pd
from pkg_resources import resource_filename

### Inputs

from name_matching_cleaning import get_accepted_info_from_names_in_column, COL_NAMES, \
    compile_hits, remove_whitespace
from powo_searches import search_powo, create_presence_absence_data

inputs_path = resource_filename(__name__, 'inputs')
morph_input_csv = os.path.join(inputs_path, '18455.txt')
emergence_input_csv = os.path.join(inputs_path, 'emergence_data.csv')
latex_input_csv = os.path.join(inputs_path, 'latex_data.csv')
corolla_input_csv = os.path.join(inputs_path, 'corolla_data.csv')
manual_morph_data_csv = os.path.join(inputs_path, 'manual_morphological_traits.csv')
### Temp outputs

temp_outputs_path = resource_filename(__name__, 'temp_outputs')

spine_temp_output_accepted_csv = os.path.join(temp_outputs_path, 'spines_try' + '_accepted.csv')
hair_temp_output_accepted_csv = os.path.join(temp_outputs_path, 'hairs_try' + '_accepted.csv')

spine_powo_search_temp_output_accepted_csv = os.path.join(temp_outputs_path, 'spines_powo' + '_accepted.csv')
hairs_powo_search_temp_output_accepted_csv = os.path.join(temp_outputs_path, 'hairs_powo' + '_accepted.csv')

manual_data_accepted_temp_output = os.path.join(temp_outputs_path, 'manual_data_accepted.csv')
manual_data_accepted_clean_temp_output = os.path.join(temp_outputs_path, 'manual_data_clean_accepted.csv')
manual_spines_output_csv = os.path.join(temp_outputs_path, 'manual_spines_hits.csv')
manual_no_spines_output_csv = os.path.join(temp_outputs_path, 'manual_no_spines_hits.csv')

### Outputs
output_path = resource_filename(__name__, 'outputs')
spines_output_csv = os.path.join(output_path, 'spines_hits.csv')
no_spines_output_csv = os.path.join(output_path, 'no_spines_hits.csv')

hairy_output_csv = os.path.join(output_path, 'hairy_hits.csv')
non_coloured_latex_output_csv = os.path.join(output_path, 'non_coloured_latex.csv')
coloured_latex_output_csv = os.path.join(output_path, 'coloured_latex.csv')
left_corollas_latex_output_csv = os.path.join(output_path, 'left_corollas.csv')
right_corollas_latex_output_csv = os.path.join(output_path, 'right_corollas.csv')
habits_output_csv = os.path.join(output_path, 'habits.csv')

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
    morph_data = morph_data.dropna(subset=['TraitName'])

    morph_data = morph_data.drop(columns=cols_to_drop)

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


def get_accepted_info_try_hair_hits():
    emergence_db = pd.read_csv(emergence_input_csv)
    emergence_db = emergence_db.dropna(subset=['OrigValueStr'])

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

    hair_try_acc = get_accepted_info_from_names_in_column(hair_db, 'AccSpeciesName')
    clean_accepted_try_hits(hair_try_acc)
    hair_try_acc.to_csv(hair_temp_output_accepted_csv)


def get_accepted_try_info_spine_hits():
    emergence_db = pd.read_csv(emergence_input_csv)
    emergence_db = emergence_db.dropna(subset=['OrigValueStr'])

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

    spine_try_acc = get_accepted_info_from_names_in_column(spine_db, 'AccSpeciesName')
    clean_accepted_try_hits(spine_try_acc)
    spine_try_acc.to_csv(spine_temp_output_accepted_csv)


def clean_accepted_try_hits(df: pd.DataFrame):
    df['OrigUnitStr'].fillna('', inplace=True)
    df['try_Snippet'] = df['DataName'] + ':' + df['OrigValueStr'] + df[
        'OrigUnitStr']
    df[COL_NAMES['single_source']] = 'TRY (' + df['Reference'] + ')'


def get_powo_spine_hits():
    search_powo(['spine', 'thorn', 'spikes'],
                spine_powo_search_temp_output_accepted_csv,
                characteristics_to_search=['leaf', 'inflorescence', 'appearance', 'fruit'],
                families_of_interest=['Rubiaceae', 'Apocynaceae'], filters=['genera', 'species', 'infraspecies'])


def get_powo_hair_hits():
    search_powo(['hairs', 'hairy', 'pubescent'],
                hairs_powo_search_temp_output_accepted_csv,
                characteristics_to_search=['leaf', 'inflorescence', 'appearance'],
                families_of_interest=['Rubiaceae', 'Apocynaceae'], filters=['genera', 'species', 'infraspecies'])


def prepare_manually_collected_data():
    manual_data = pd.read_csv(manual_morph_data_csv)
    manual_data.drop(columns='Comment', inplace=True)
    manual_data.rename(columns={'spines (present (y) or absent(x)': 'spines',
                                'latex (white, clear, red, orange, yellow)': 'latex',
                                'corolla overlap (left (l) or right(r))': 'corolla',
                                'predominant habit (shrub (sh), subshrub (subsh), liana (li), tree(tr), succ (sc), herb (hb)': 'habit'
                                }, inplace=True)
    manual_data['Source'] = 'Manual check'
    manual_data['Manual_snippet'] = ''
    manual_data['spines'] = manual_data['spines'].apply(remove_whitespace)
    manual_data['latex'] = manual_data['latex'].apply(remove_whitespace)
    manual_data['corolla'] = manual_data['corolla'].apply(remove_whitespace)
    manual_data['habit'] = manual_data['habit'].apply(remove_whitespace)

    acc_manual_data = get_accepted_info_from_names_in_column(manual_data, 'Genera')

    acc_manual_data.to_csv(manual_data_accepted_clean_temp_output)

    # Spines
    spines = acc_manual_data[acc_manual_data['spines'] == 'y']
    no_spines = acc_manual_data[acc_manual_data['spines'] == 'x']

    spines.to_csv(manual_spines_output_csv)
    no_spines.to_csv(manual_no_spines_output_csv)


def get_data():
    clean_try_db()
    get_accepted_try_info_spine_hits()
    get_accepted_info_try_hair_hits()

    prepare_manually_collected_data()

    get_powo_spine_hits()
    get_powo_hair_hits()


def output_compiled_data():
    # Spines
    powo_spine_hits = pd.read_csv(spine_powo_search_temp_output_accepted_csv)

    # Spines are often reported as 'absent'
    # List accepted ids of such cases to remove
    spine_ids_for_absence = ['34290-1', '2257-1', '2425-1', '2469-1', '2560-1', '331696-2', '2171-1',
                             '2218-1',
                             '2298-1',
                             '2180-1',
                             '2516-1',
                             '2198-1',
                             '2377-1', '328992-2'
                             ]
    powo_presence_spine_hits, powo_absence_spine_hits = create_presence_absence_data(powo_spine_hits,
                                                                                     accepted_ids_of_absence=spine_ids_for_absence)

    try_spine_hits = pd.read_csv(spine_temp_output_accepted_csv)
    manual_spine_hits = pd.read_csv(manual_spines_output_csv)
    all_spine_dfs = [manual_spine_hits, try_spine_hits, powo_presence_spine_hits]
    compile_hits(all_spine_dfs, spines_output_csv)

    manual_no_spines_hits = pd.read_csv(manual_no_spines_output_csv)
    compile_hits([powo_absence_spine_hits, manual_no_spines_hits], no_spines_output_csv)

    # Hairs
    powo_hair_hits = pd.read_csv(hairs_powo_search_temp_output_accepted_csv)
    try_hair_hits = pd.read_csv(hair_temp_output_accepted_csv)

    all_hair_hits = [powo_hair_hits, try_hair_hits]
    compile_hits(all_hair_hits, hairy_output_csv)

    # Latex
    acc_manual_data = pd.read_csv(manual_data_accepted_clean_temp_output)
    non_coloured_latex = acc_manual_data[
        (acc_manual_data['latex'].isin(['w', 'c']))]
    compile_hits([non_coloured_latex], non_coloured_latex_output_csv)
    coloured_latex = acc_manual_data[
        acc_manual_data['latex'].isin(['w/y', 'w/r', 'r/y/w', 'r/o/y'])]
    compile_hits([coloured_latex], coloured_latex_output_csv)

    # Corollas
    left_corollas = acc_manual_data[
        (acc_manual_data['corolla'].isin(['l']))]
    compile_hits([left_corollas], left_corollas_latex_output_csv)
    right_corollas = acc_manual_data[
        acc_manual_data['corolla'].isin(['r'])]
    compile_hits([right_corollas], right_corollas_latex_output_csv)

    # Habit
    habits = acc_manual_data.drop(columns=[
        'spines',
        'latex',
        'corolla', 'Manual_snippet'])
    habits = habits.rename(columns={'habit': 'Manual_snippet'})
    habits.to_csv(habits_output_csv)


def main():
    # get_data()
    output_compiled_data()


if __name__ == '__main__':
    main()
