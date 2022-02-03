import hashlib
import os

import pandas as pd
import requests
from typing import List

from pkg_resources import resource_filename
from tqdm import tqdm

from name_matching_cleaning import get_accepted_info_from_names_in_column
from taxa_lists import get_all_taxa

_temp_outputs_path = resource_filename(__name__, 'temp_outputs')
outputs_path = resource_filename(__name__, 'outputs')
rubiaceae_apocynaceae_metabolites_output_csv = os.path.join(outputs_path, 'rub_apocs_metabolites.csv')


def get_metabolites_for_taxon(name: str):
    url_name_format = name.replace(' ', '%20')

    url = f'http://www.knapsackfamily.com/knapsack_core/result.php?sname=organism&word={url_name_format}'
    tables = pd.read_html(url, flavor='html5lib')
    taxa_table = tables[0]
    metabolites = taxa_table['Metabolite'].values.tolist()

    return metabolites


def get_metabolites_for_taxa(taxa_list: List[str], output_csv: str = None, force_new_search=False) -> pd.DataFrame:
    if not os.path.isdir(_temp_outputs_path):
        os.mkdir(_temp_outputs_path)
    if not os.path.isdir(outputs_path):
        os.mkdir(outputs_path)

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
        for i in tqdm(range(len(taxa_list)), desc="Searching for knapsack Pages…", ascii=False, ncols=72):
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
        check_csv = os.path.join(_temp_outputs_path, 'taxa_to_recheck.csv')
        check_df.to_csv(check_csv)
        print(
            f'Warning {str(len(unchecked_taxa_due_to_timeout))} taxa were unchecked due to server timeouts. Rerun search for taxa in {check_csv}')


    df.to_csv(temp_output_metabolite_csv)

    acc_df = get_accepted_info_from_names_in_column(df, 'taxa')

    acc_df.to_csv(output_csv)
    return acc_df


def main():

    data = get_all_taxa(families_of_interest=['Apocynaceae', 'Rubiaceae'], accepted=True)

    ranks_to_use = ["Species", "Variety", "Subspecies"]

    taxa = data.loc[data["rank"].isin(ranks_to_use)]

    taxa_list = taxa["taxon_name"].values

    get_metabolites_for_taxa(taxa_list, output_csv=rubiaceae_apocynaceae_metabolites_output_csv)


if __name__ == '__main__':
    main()
