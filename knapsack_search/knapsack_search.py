import hashlib
import os

import numpy as np
import pandas as pd
import requests
from typing import List

from pkg_resources import resource_filename
from tqdm import tqdm

from name_matching_cleaning import get_accepted_info_from_names_in_column
from taxa_lists import get_all_taxa

_inputs_path = resource_filename(__name__, 'inputs')
_temp_outputs_path = resource_filename(__name__, 'temp_outputs')
_check_csv = os.path.join(_temp_outputs_path, 'taxa_to_recheck.csv')
_outputs_path = resource_filename(__name__, 'outputs')
rubiaceae_apocynaceae_metabolites_output_csv = os.path.join(_outputs_path, 'rub_apocs_metabolites.csv')
rubiaceae_apocynaceae_alks_output_csv = os.path.join(_outputs_path, 'rub_apocs_alkaloids.csv')
rub_apoc_alkaloid_hits_output_csv = os.path.join(_outputs_path, 'rub_apocs_alkaloid_hits.csv')
rub_apoc_antibac_metabolites_output_csv = os.path.join(_outputs_path, 'rub_apocs_antibac_metabolites.csv')
_check_output_csv = os.path.join(_outputs_path, 'rechecked_taxa.csv')


def get_antibacterial_metabolites():
    antibac_table = pd.read_html(os.path.join(_inputs_path, 'antibacterialmetabolites.html'), flavor='html5lib')[0]
    antibac_table = antibac_table[antibac_table['Biological Activity (Function)'] != 'Antibacterial inactive']
    antibac_table = antibac_table.dropna(subset=['Metabolite Name'])
    return antibac_table['Metabolite Name'].unique().tolist()


def get_antimalarial_metabolites():
    antimal_table = pd.read_html(os.path.join(_inputs_path, 'antimalarialmetabolites.html'), flavor='html5lib')[0]
    antimal_table = antimal_table[antimal_table['Biological Activity (Function)'] != 'Antimalarial inactive']
    antimal_table = antimal_table.dropna(subset=['Metabolite Name'])
    return antimal_table['Metabolite Name'].unique().tolist()


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

        return formulas
    except (KeyError, IndexError):
        print(f'Warning: No info found for {metabolite}')
        return []


def get_metabolites_for_taxon(name: str):
    url_name_format = name.replace(' ', '%20')

    url = f'http://www.knapsackfamily.com/knapsack_core/result.php?sname=organism&word={url_name_format}'
    try:

        tables = pd.read_html(url, flavor='html5lib')

    except UnicodeEncodeError:
        response = requests.get(url)
        decoded = response.content.decode()
        tables = pd.read_html(decoded, flavor='html5lib')
    taxa_table = tables[0]
    metabolites = taxa_table['Metabolite'].values.tolist()

    return metabolites


def get_metabolites_for_taxa(taxa_list: List[str], output_csv: str = None, force_new_search=False) -> pd.DataFrame:
    if not os.path.isdir(_temp_outputs_path):
        os.mkdir(_temp_outputs_path)
    if output_csv is not None:
        if not os.path.isdir(os.path.dirname(output_csv)):
            os.mkdir(os.path.dirname(output_csv))

    # Save previous searches using a hash of names to avoid repeating searches
    names = list(taxa_list)
    str_to_hash = str(names).encode()
    temp_csv = "knap_metabolite_search_" + str(hashlib.md5(str_to_hash).hexdigest()) + ".csv"

    temp_output_metabolite_csv = os.path.join(_temp_outputs_path, temp_csv)
    unchecked_taxa_due_to_timeout = []
    if os.path.isfile(temp_output_metabolite_csv) and not force_new_search:

        df = pd.read_csv(temp_output_metabolite_csv)
    else:
        all_metabolites = []
        prelim_dict = {}
        for i in tqdm(range(len(taxa_list)), desc="Searching Knapsack…", ascii=False, ncols=80):
            sp = taxa_list[i]

            try:
                metas = get_metabolites_for_taxon(sp)
                prelim_dict[sp] = metas
                for m in metas:
                    if m not in all_metabolites:
                        all_metabolites.append(m)
            except:
                unchecked_taxa_due_to_timeout.append(sp)

        out_dict = {'taxa': []}
        for m in all_metabolites:
            out_dict[m] = []
        for sp in prelim_dict:
            out_dict['taxa'].append(sp)
            for m in all_metabolites:
                if m in prelim_dict[sp]:
                    out_dict[m].append(1)
                else:
                    out_dict[m].append(0)

        df = pd.DataFrame(out_dict)

    if len(unchecked_taxa_due_to_timeout) > 0:
        taxa_to_check_dict = {'taxa': unchecked_taxa_due_to_timeout}
        check_df = pd.DataFrame(taxa_to_check_dict)

        check_df.to_csv(_check_csv)
        print(
            f'Warning {str(len(unchecked_taxa_due_to_timeout))} taxa were unchecked due to server timeouts.')
        print(f'Rerun search for taxa in {_check_csv}')

    df.to_csv(temp_output_metabolite_csv)

    acc_df = get_accepted_info_from_names_in_column(df, 'taxa')

    acc_df.to_csv(output_csv)
    return acc_df


def recheck_taxa():
    taxa = pd.read_csv(_check_csv)
    taxa_list = taxa['taxa'].values
    get_metabolites_for_taxa(taxa_list, output_csv=_check_output_csv)


def summarise_metabolites():
    metas_data = pd.read_csv(rubiaceae_apocynaceae_metabolites_output_csv)
    summ = metas_data.describe()
    print(summ)
    worthwhile_metabolites = [x for x in summ.columns if summ[x]['mean'] > 0.001]
    print(worthwhile_metabolites)


def get_antibac_metabolite_hits_for_taxa(taxa_metabolite_data: pd.DataFrame, output_csv: str, fams: List[str] = None):
    """

    :param taxa_metabolite_data: Dataframe with taxa in first column and metabolites in the rest of the columns
    with 1's and 0's in cells indicating presence of metabolite
    :param output_csv:
    :return:
    """
    antibac_metabolites = get_antibacterial_metabolites()

    out_dict = {'taxa': [], 'knapsack_snippet': []}
    for i in tqdm(range(len(taxa_metabolite_data['taxa'].values)), desc="Searching...", ascii=False, ncols=72):
        taxa = taxa_metabolite_data['taxa'].values[i]

        taxa_record = taxa_metabolite_data[taxa_metabolite_data['taxa'] == taxa]
        # print(taxa_record.columns)
        metabolites_in_taxa = [x for x in taxa_record.columns if taxa_record[x].iloc[0] == 1]

        antibac_metabolites_in_taxa = []
        for metabolite in metabolites_in_taxa:
            if metabolite in antibac_metabolites:
                antibac_metabolites_in_taxa.append(metabolite)

        if len(antibac_metabolites_in_taxa) > 0:
            out_dict['taxa'].append(taxa)

            out_dict['knapsack_snippet'].append('"' + str(antibac_metabolites_in_taxa) + '"')
    out_df = pd.DataFrame(out_dict)
    out_df["Source"] = "KNApSAcK"

    acc_df = get_accepted_info_from_names_in_column(out_df, 'taxa', families_of_interest=fams)

    acc_df.to_csv(output_csv)


def get_alkaloids_from_metabolites(metabolites_to_check: List[str], output_csv: str):
    """ Ends in 'ine' usually indicates alkaloid
        Must contain nitrogen
    """

    alkaloid_metabolites = []
    suffixes = ["ine-", "ine ", "ine+", "ine("]
    known_non_alkaloids = []
    for i in tqdm(range(len(metabolites_to_check)), desc="Searching for alks", ascii=False, ncols=72):
        m = metabolites_to_check[i]
        if m not in known_non_alkaloids:
            if any(s in m for s in suffixes) or m.endswith('ine'):
                formulas = get_formulas_for_metabolite(m)
                if all("N" in f for f in formulas):
                    alkaloid_metabolites.append(m)
    out_dict = {'alks': alkaloid_metabolites}

    out_df = pd.DataFrame(out_dict)
    out_df["Reason"] = "Contains Nitrogen and ine at end of word"
    out_df["Source"] = "KNApSAcK"
    out_df.to_csv(output_csv)

    return out_df


def get_alkaloid_hits_for_taxa(taxa_metabolite_data: pd.DataFrame, alkaloid_df: pd.DataFrame, output_csv: str,
                               fams: List[str] = None):
    """

    :param taxa_metabolite_data: Dataframe with taxa in first column and metabolites in the rest of the columns
    with 1's and 0's in cells indicating presence of metabolite
    :param alkaloid_df:
    :param output_csv:
    :return:
    """
    alks = alkaloid_df['alks'].values.tolist()
    out_dict = {'taxa': [], 'knapsack_snippet': []}
    for i in tqdm(range(len(taxa_metabolite_data['taxa'].values)), desc="Searching...", ascii=False, ncols=72):
        taxa = taxa_metabolite_data['taxa'].values[i]

        taxa_record = taxa_metabolite_data[taxa_metabolite_data['taxa'] == taxa]
        # print(taxa_record.columns)
        metabolites_in_taxa = [x for x in taxa_record.columns if taxa_record[x].iloc[0] == 1]

        alk_metabolites_in_taxa = []
        for metabolite in metabolites_in_taxa:
            if metabolite in alks:
                alk_metabolites_in_taxa.append(metabolite)

        if len(alk_metabolites_in_taxa) > 0:
            out_dict['taxa'].append(taxa)

            out_dict['knapsack_snippet'].append('"' + str(alk_metabolites_in_taxa) + '"')
    out_df = pd.DataFrame(out_dict)
    out_df["Source"] = "KNApSAcK"

    acc_df = get_accepted_info_from_names_in_column(out_df, 'taxa', families_of_interest=fams)

    acc_df.to_csv(output_csv)
    return acc_df


def get_rub_apoc_antibac_metabolite_hits():
    all_metas_data = pd.read_csv(rubiaceae_apocynaceae_metabolites_output_csv)
    get_antibac_metabolite_hits_for_taxa(all_metas_data, rub_apoc_antibac_metabolites_output_csv,
                                         fams=['Rubiaceae', 'Apocynaceae'])


def get_rub_apoc_metabolites():
    data = get_all_taxa(families_of_interest=['Apocynaceae', 'Rubiaceae'], accepted=True)

    ranks_to_use = ["Species", "Variety", "Subspecies"]

    taxa = data.loc[data["rank"].isin(ranks_to_use)]

    taxa_list = taxa["taxon_name"].values

    get_metabolites_for_taxa(taxa_list, output_csv=rubiaceae_apocynaceae_metabolites_output_csv)


def get_rub_apoc_alkaloid_hits():
    metabolites_to_check = pd.read_csv(rubiaceae_apocynaceae_metabolites_output_csv).columns.tolist()

    alks_df = get_alkaloids_from_metabolites(metabolites_to_check, rubiaceae_apocynaceae_alks_output_csv)

    rubs_apoc_metas_data = pd.read_csv(rubiaceae_apocynaceae_metabolites_output_csv)
    get_alkaloid_hits_for_taxa(rubs_apoc_metas_data, alks_df, rub_apoc_alkaloid_hits_output_csv,
                               fams=['Rubiaceae', 'Apocynaceae'])


def main():
    get_rub_apoc_metabolites()
    recheck_taxa()
    summarise_metabolites()
    get_rub_apoc_antibac_metabolite_hits()
    get_rub_apoc_alkaloid_hits()


if __name__ == '__main__':
    alks_df = pd.read_csv(rubiaceae_apocynaceae_alks_output_csv)
    rubs_apoc_metas_data = pd.read_csv(rubiaceae_apocynaceae_metabolites_output_csv)
    get_alkaloid_hits_for_taxa(rubs_apoc_metas_data, alks_df, rub_apoc_alkaloid_hits_output_csv,
                               fams=['Rubiaceae', 'Apocynaceae'])
