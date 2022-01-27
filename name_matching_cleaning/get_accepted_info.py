import json

import numpy as np
import pykew.powo as powo
import pandas as pd
import requests
from pkg_resources import resource_filename
from typing import List

from name_matching_cleaning import clean_urn_ids
from taxa_lists.get_taxa_from_wcvp import get_all_taxa

inputs_path = resource_filename(__name__, 'inputs')

temp_outputs = resource_filename(__name__, 'temp_outputs')


def search_ipni():
    import pykew.ipni as ipni

    result = ipni.search('Poa annua')
    print(result)
    d = pd.DataFrame(result._response['results'])
    d.to_csv('test.csv')


def id_lookup_powo(id: str):
    base = "urn:lsid:ipni.org:names:"
    full_id = base + str(id)
    r = powo.lookup(full_id)

    print(r)


def id_lookup_wcvp(all_taxa: pd.DataFrame, given_id: str, dict_to_update: dict = None) -> dict:
    if "urn:lsid:ipni.org:names:" in given_id:
        given_id = clean_urn_ids(given_id)
    record = all_taxa[all_taxa['kew_id'] == given_id]
    if len(record.index) == 0:
        raise KeyError(f"Can't find id: {given_id} in given wcvp taxa data")
    elif len(record.index) > 1:
        raise ValueError(f"Multiple id matches found in given wcvp data for id: {given_id}")
    record.reset_index(inplace=True)
    print(record)
    taxonomic_status = record.at[0, 'taxonomic_status']
    if taxonomic_status == 'Accepted':
        Accepted_Name = record.at[0, 'taxon_name']
        Accepted_ID = record.at[0, 'kew_id']
    else:
        Accepted_Name = record.at[0, 'accepted_name']
        Accepted_ID = record.at[0, 'accepted_kew_id']
    Accepted_Rank = record.at[0, 'rank']

    if Accepted_Rank == "SPECIES":
        Accepted_Species = Accepted_Name
        Accepted_Species_ID = Accepted_ID
    else:
        Accepted_Species = record.at[0, 'parent_name']
        Accepted_Species_ID = record.at[0, 'parent_kew_id']

    if dict_to_update is not None:
        dict_to_update['Accepted_Name'].append(Accepted_Name)
        dict_to_update['Accepted_ID'].append(Accepted_ID)
        dict_to_update['Accepted_Rank'].append(Accepted_Rank)
        dict_to_update['Accepted_Species'].append(Accepted_Species)
        dict_to_update['Accepted_Species_ID'].append(Accepted_Species_ID)

    print(given_id)
    print(dict_to_update)
    return {'Accepted_Name': Accepted_Name, 'Accepted_ID': Accepted_ID, 'Accepted_Rank': Accepted_Rank,
            'Accepted_Species': Accepted_Species, 'Accepted_Species_ID': Accepted_Species_ID}


def get_accepted_info_from_ids_in_column(all_taxa: pd.DataFrame, df: pd.DataFrame, id_col_name: str):
    """
    Appends accepted info columns to df, based on ids in id_col_name
    :param all_taxa:
    :param df:
    :param id_col_name:
    :return:
    """
    dict_of_values = {'Accepted_Name': [], 'Accepted_ID': [], 'Accepted_Rank': [],
                      'Accepted_Species': [], 'Accepted_Species_ID': []}
    [id_lookup_wcvp(all_taxa, x, dict_of_values) for x in df[id_col_name].values]
    print(dict_of_values)

    match_df = pd.DataFrame(dict_of_values)

    return pd.concat([df, match_df], axis=1)


def find_best_match(multiple_match_records: pd.DataFrame, families_of_interest=None) -> pd.DataFrame:
    """
    Gets best matching for each submitted match and returns a dataframe of single matches
    """
    wcvp_taxa = get_all_taxa(families_of_interest=families_of_interest)
    multiple_match_records['ipni_id'] = multiple_match_records['ipni_id'].apply(clean_urn_ids)
    multiple_matches_with_accepted_ids = get_accepted_info_from_ids_in_column(wcvp_taxa, multiple_match_records,
                                                                              'ipni_id')


    pass
    # match_df['submitted'] = df['submitted']
    #
    # accepted_names_matching_submitted_names = match_df[match_df['submitted'] == match_df['Accepted_Name']]
    # submitted_names_with_single_accepted_match = match_df.drop_duplicates(subset=['submitted'], keep=False)
    #
    # matches_to_use = pd.concat([accepted_names_matching_submitted_names, submitted_names_with_single_accepted_match])
    # matches_to_use.drop_duplicates('Accepted_ID',inplace=True)


def knms_match_names(names: List[str]):
    knms_url = "http://namematch.science.kew.org/api/v2/powo/match"
    res = requests.post(knms_url, json=names)
    headings = ['submitted', 'match_state', 'ipni_id', 'matched_name']

    content = json.loads(res.content.decode('utf-8'))
    records = pd.DataFrame(content["records"], columns=headings)
    records.replace('', np.nan, inplace=True)
    records['submitted'].ffill(inplace=True)
    records['match_state'].ffill(inplace=True)

    records.to_csv('allm.csv')
    multiple_matches = records[records['match_state'] == 'multiple_matches']
    multiple_matches.to_csv('testmm.csv')
    print(res)


def get_matched_names_from_names_in_column(df: pd.DataFrame, name_col: str):
    pass


if __name__ == '__main__':
    # knms_match_names(['Poa annua','Aspidosperma'])
    mm = pd.read_csv('testmm.csv')
    print(mm.columns)
    find_best_match(mm)
    # id_lookup_powo('44583-2')
    # id_lookup_wcvp('77210192-1')
