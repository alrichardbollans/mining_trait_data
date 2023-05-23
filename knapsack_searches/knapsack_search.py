import os
import time

import pandas as pd
import requests
from pkg_resources import resource_filename
from tqdm import tqdm
from wcvp_download import get_all_taxa, wcvp_columns, wcvp_accepted_columns
from wcvp_name_matching import get_accepted_info_from_names_in_column

_inputs_path = resource_filename(__name__, 'inputs')
_temp_outputs_path = resource_filename(__name__, 'temp_outputs')
_check_csv = os.path.join(_temp_outputs_path, 'taxa_to_recheck.csv')
_outputs_path = resource_filename(__name__, 'outputs')

kn_metabolite_name_column = 'Metabolite'
kn_formula_column = 'Molecular formula'
kn_organism_column = 'Organism'


def get_metabolites_for_taxon(name: str):
    # Note that this is greedy as name matches in Knapsack search include partial e.g. Cissus matches Narcissus
    url_name_format = name.replace(' ', '%20')

    url = f'http://www.knapsackfamily.com/knapsack_core/result.php?sname=organism&word={url_name_format}'
    try:
        time.sleep(.01)
        tables = pd.read_html(url, flavor='html5lib')

    except UnicodeEncodeError:
        response = requests.get(url)
        decoded = response.content.decode()
        tables = pd.read_html(decoded, flavor='html5lib')
    metabolite_table = tables[0]
    metabolite_table['search_term'] = name

    return metabolite_table


def get_metabolites_in_family(family: str, temp_output_csv: str = None, output_csv: str = None):
    # Note that this is greedy as name matches in Knapsack search include partial e.g. Cissus matches Narcissus
    # Account for this by removing results without name resolution
    wcvp_data = get_all_taxa(families_of_interest=[family])
    if output_csv is not None:
        if not os.path.isdir(os.path.dirname(output_csv)):
            os.mkdir(os.path.dirname(output_csv))

    # Search family by looking for all data from genera
    genera_list = wcvp_data[wcvp_columns['genus']].unique()
    failed_genera = []
    all_genera_df = pd.DataFrame()
    for i in tqdm(range(len(genera_list)), desc="Searching genera in Knapsack…", ascii=False, ncols=80):
        genus = genera_list[i]
        try:
            genus_table = get_metabolites_for_taxon(genus)
            if len(genus_table.index) > 0:
                all_genera_df = pd.concat([all_genera_df, genus_table])
        except:
            failed_genera.append(genus)
    if temp_output_csv is not None:
        all_genera_df.to_csv(temp_output_csv)

    acc_df = get_accepted_info_from_names_in_column(all_genera_df, 'Organism',
                                                    manual_resolution_csv=os.path.join(_inputs_path,
                                                                                       'manual_match_data.csv'), )
    acc_df = acc_df[acc_df[wcvp_accepted_columns['family']] == family]
    acc_df['Source'] = 'KNApSAcK'
    acc_df['knapsack_snippet'] = acc_df[kn_metabolite_name_column]
    acc_df.to_csv(output_csv)
    if len(failed_genera) > 0:
        print('WARNING: Searching for the following genera raised an error and should be manually checked:')
        print(failed_genera)
        raise ValueError
    return acc_df


def get_formulas_for_metabolite(metabolite: str):
    url_name_format = metabolite.replace(' ', '%20')
    url_name_format = url_name_format.replace('+', 'plus')
    url = f'http://www.knapsackfamily.com/knapsack_core/result.php?sname=metabolite&word={url_name_format}'
    try:

        tables = pd.read_html(url, flavor='html5lib')

    except UnicodeEncodeError:
        response = requests.get(url)
        decoded = response.content.decode()
        tables = pd.read_html(decoded, flavor='html5lib')
    meta_table = tables[0]
    try:
        formulas = meta_table['Molecular formula'].values.tolist()
        if formulas == []:
            print(f'Warning: No info found for {metabolite}')
        return formulas
    except (KeyError, IndexError):
        print(f'Warning: No info found for {metabolite}')
        return []
