import numpy as np
import pandas as pd

from name_matching_cleaning import clean_urn_ids
from taxa_lists import get_all_taxa


def _get_dict_from_wcvp_record(record: pd.DataFrame) -> dict:
    """
    Formats a record from wcvp into a dictionary to integrate into other data
    :param record:
    :return:
    """
    taxonomic_status = record['taxonomic_status'].values[0]
    if taxonomic_status == 'Accepted':
        Accepted_Name = record['taxon_name'].values[0]
        Accepted_ID = record['kew_id'].values[0]
    else:
        Accepted_Name = record['accepted_name'].values[0]
        Accepted_ID = record['accepted_kew_id'].values[0]
    Accepted_Rank = record['rank'].values[0]

    if Accepted_Rank == "Species":
        Accepted_Species = Accepted_Name
        Accepted_Species_ID = Accepted_ID
    else:
        Accepted_Species = record['parent_name'].values[0]
        Accepted_Species_ID = record['parent_kew_id'].values[0]

    return {'Accepted_Name': Accepted_Name, 'Accepted_ID': Accepted_ID, 'Accepted_Rank': Accepted_Rank,
            'Accepted_Species': Accepted_Species, 'Accepted_Species_ID': Accepted_Species_ID}


def _name_lookup_wcvp(all_taxa: pd.DataFrame, given_name: str) -> dict:
    """
    Looks for name in list of taxa, returns a dictionary of accepted information
    :param all_taxa:
    :param given_name:
    :return:
    """
    given_name = str(given_name)
    record = all_taxa[all_taxa['taxon_name'] == given_name]
    nan_dict = {'Accepted_Name': np.nan, 'Accepted_ID': np.nan, 'Accepted_Rank': np.nan,
                'Accepted_Species': np.nan, 'Accepted_Species_ID': np.nan}
    if len(record.index) == 0:
        print(f"Can't find name: {given_name} in given wcvp taxa data")
        return nan_dict
    if len(record.index) > 1:
        print(
            f"Multiple matches found in given wcvp data for name: {given_name}. Attempting to find accepted name match...")

        record = all_taxa[all_taxa['accepted_name'] == given_name]
        if len(record.index) == 1:
            print("Found accepted name match")
            return _get_dict_from_wcvp_record(record)
        print("Unique accepted name match not found")
        return nan_dict
    return _get_dict_from_wcvp_record(record)


def id_lookup_wcvp(all_taxa: pd.DataFrame, given_id: str) -> dict:
    """
    Looks for id in list of taxa, returns a dictionary of accepted information
    :param all_taxa:
    :param given_id:
    :return:
    """
    given_id = str(given_id)
    if "urn:lsid:ipni.org:names:" in given_id:
        given_id = clean_urn_ids(given_id)
    record = all_taxa[all_taxa['kew_id'] == given_id]
    nan_dict = {'Accepted_Name': np.nan, 'Accepted_ID': np.nan, 'Accepted_Rank': np.nan,
                'Accepted_Species': np.nan, 'Accepted_Species_ID': np.nan}
    if len(record.index) == 0:
        nan_dict = {'Accepted_Name': np.nan, 'Accepted_ID': np.nan, 'Accepted_Rank': np.nan,
                    'Accepted_Species': np.nan, 'Accepted_Species_ID': np.nan}
        print(f"Can't find id: {given_id} in given wcvp taxa data")
        return nan_dict
    if len(record.index) > 1:
        print(f"Multiple id matches found in given wcvp data for id: {given_id}")
        return nan_dict
    return _get_dict_from_wcvp_record(record)


def get_wcvp_info_for_names_in_column(df: pd.DataFrame, name_col: str, all_taxa: pd.DataFrame = None):
    """
    Appends accepted info columns to df from list of taxa, based on names in name_col
    :param df:
    :param name_col:
    :param all_taxa:
    :return:
    """
    if all_taxa is None:
        all_taxa = get_all_taxa()

    dict_of_values = {'Accepted_Name': [], 'Accepted_ID': [], 'Accepted_Rank': [],
                      'Accepted_Species': [], 'Accepted_Species_ID': []}
    for x in df[name_col].values:
        acc_info = _name_lookup_wcvp(all_taxa, x)
        for k in dict_of_values:
            dict_of_values[k].append(acc_info[k])

    match_df = pd.DataFrame(dict_of_values)
    # Set indices for concatenating properly
    match_df.set_index(df.index, inplace=True)
    return pd.concat([df, match_df], axis=1)
