import hashlib
import os
import time

import html5lib
import pandas as pd
import requests
from typing import List

from pkg_resources import resource_filename
from tqdm import tqdm

from automatchnames import get_accepted_info_from_names_in_column
from taxa_lists import get_all_taxa

from metabolite_searches import get_antibacterial_metabolites, get_alkaloids_from_metabolites, \
    get_steroids_from_metabolites, get_cardenolides_from_metabolites

_inputs_path = resource_filename(__name__, 'inputs')
_temp_outputs_path = resource_filename(__name__, 'temp_outputs')
_check_csv = os.path.join(_temp_outputs_path, 'taxa_to_recheck.csv')
_outputs_path = resource_filename(__name__, 'outputs')


def get_metabolites_for_taxon(name: str):
    url_name_format = name.replace(' ', '%20')

    url = f'http://www.knapsackfamily.com/knapsack_core/result.php?sname=organism&word={url_name_format}'
    try:
        time.sleep(.01)
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
            except Exception as e:
                print(e)
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


def recheck_taxa(check_output_csv: str):
    taxa = pd.read_csv(_check_csv)
    taxa_list = taxa['taxa'].values
    get_metabolites_for_taxa(taxa_list, output_csv=check_output_csv)


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


def output_alkaloids_from_metabolites(metabolites_to_check: List[str], output_csv: str):
    """ Ends in 'ine' usually indicates alkaloid
        Must contain nitrogen
    """

    alkaloid_metabolites = get_alkaloids_from_metabolites(metabolites_to_check)

    out_df = pd.DataFrame(alkaloid_metabolites)

    out_df["Source"] = "KNApSAcK"
    out_df.to_csv(output_csv)

    return out_df

def output_steroids_from_metabolites(metabolites_to_check: List[str], output_csv: str):

    steroid_metabolites = get_steroids_from_metabolites(metabolites_to_check)

    out_df = pd.DataFrame(steroid_metabolites)

    out_df["Source"] = "KNApSAcK"
    out_df.to_csv(output_csv)

    return out_df

def output_cardenolides_from_metabolites(metabolites_to_check: List[str], output_csv: str):

    cardenolides_metabolites = get_cardenolides_from_metabolites(metabolites_to_check)

    out_df = pd.DataFrame(cardenolides_metabolites)

    out_df["Source"] = "KNApSAcK"
    out_df.to_csv(output_csv)

    return out_df

def get_compound_hits_for_taxa(compound_abbv:str,taxa_metabolite_data: pd.DataFrame, compound_df: pd.DataFrame, output_csv: str,
                               fams: List[str] = None):
    """

    :param taxa_metabolite_data: Dataframe with taxa in first column and metabolites in the rest of the columns
    with 1's and 0's in cells indicating presence of metabolite
    :param alkaloid_df:
    :param output_csv:
    :return:
    """
    compound = compound_df[compound_abbv].values.tolist()
    out_dict = {'taxa': [], 'knapsack_snippet': []}
    for i in tqdm(range(len(taxa_metabolite_data['taxa'].values)), desc="Adding compound hits to taxa", ascii=False,
                  ncols=80):
        taxa = taxa_metabolite_data['taxa'].values[i]

        taxa_record = taxa_metabolite_data[taxa_metabolite_data['taxa'] == taxa]
        # print(taxa_record.columns)
        metabolites_in_taxa = [x for x in taxa_record.columns if taxa_record[x].iloc[0] == 1]

        compound_metabolites_in_taxa = []
        for metabolite in metabolites_in_taxa:
            if metabolite in compound:
                compound_metabolites_in_taxa.append(metabolite)

        if len(compound_metabolites_in_taxa) > 0:
            out_dict['taxa'].append(taxa)

            out_dict['knapsack_snippet'].append('"' + str(compound_metabolites_in_taxa) + '"')
    out_df = pd.DataFrame(out_dict)
    out_df["Source"] = "KNApSAcK"

    acc_df = get_accepted_info_from_names_in_column(out_df, 'taxa', families_of_interest=fams)

    acc_df.to_csv(output_csv)
    return acc_df

def main():
    pass


if __name__ == '__main__':
    main()
    # get_rub_apoc_alkaloid_hits()
