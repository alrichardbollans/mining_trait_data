import numpy as np
import pandas as pd
from tqdm import tqdm

from name_matching_cleaning import clean_urn_ids
from taxa_lists import get_all_taxa


def _get_dict_from_wcvp_record(record: pd.DataFrame, taxa_list: pd.DataFrame) -> dict:
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

    if Accepted_Rank in ["Synonym", "Homotypic_Synonym", "Species"]:
        Accepted_Species = Accepted_Name
        Accepted_Species_ID = Accepted_ID
    elif taxonomic_status == 'Accepted' or Accepted_Rank == "Genus":
        # Parents are only given to accepted taxa in wcvp
        Accepted_Species = record['parent_name'].values[0]
        Accepted_Species_ID = record['parent_kew_id'].values[0]

    elif Accepted_Rank in ["Variety", "Subspecies"]:
        # When subspecies and varieties are not accepted we need to find their parent
        accepted_taxon = taxa_list[(taxa_list['taxon_name'] == Accepted_Name) & (taxa_list['kew_id'] == Accepted_ID)]
        Accepted_Species = accepted_taxon['parent_name'].values[0]
        Accepted_Species_ID = accepted_taxon['parent_kew_id'].values[0]
    else:
        raise ValueError(f'Combination of status: {taxonomic_status} and rank: {Accepted_Rank} unaccounted for.')

    return {'Accepted_Name': Accepted_Name, 'Accepted_ID': Accepted_ID, 'Accepted_Rank': Accepted_Rank,
            'Accepted_Species': Accepted_Species, 'Accepted_Species_ID': Accepted_Species_ID}


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
    return _get_dict_from_wcvp_record(record, all_taxa)


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

    taxa_in_df = all_taxa[all_taxa['taxon_name'].isin(df[name_col])]

    renaming = {'accepted_name': 'Accepted_Name', 'accepted_kew_id': 'Accepted_ID', 'rank': 'Accepted_Rank',
                'parent_name': 'Accepted_Species', 'parent_kew_id': 'Accepted_Species_ID'}

    renamed_taxa_cols = taxa_in_df.rename(columns=renaming)
    # Put accepted names and ids in columns for accepted taxa as otherwise they are nan
    renamed_taxa_cols.loc[renamed_taxa_cols['taxonomic_status'] == 'Accepted', 'Accepted_Name'] = \
        renamed_taxa_cols[renamed_taxa_cols['taxonomic_status'] == 'Accepted']['taxon_name']

    renamed_taxa_cols.loc[renamed_taxa_cols['taxonomic_status'] == 'Accepted', 'Accepted_ID'] = \
        renamed_taxa_cols[renamed_taxa_cols['taxonomic_status'] == 'Accepted']['kew_id']

    renamed_taxa_cols.loc[renamed_taxa_cols['Accepted_Rank'] == 'Species', 'Accepted_Species'] = \
        renamed_taxa_cols[renamed_taxa_cols['Accepted_Rank'] == 'Species']['Accepted_Name']

    renamed_taxa_cols.loc[renamed_taxa_cols['Accepted_Rank'] == 'Species', 'Accepted_Species_ID'] = \
        renamed_taxa_cols[renamed_taxa_cols['Accepted_Rank'] == 'Species']['Accepted_ID']

    status_priority = ["Accepted", "Synonym", "Homotypic_Synonym"]
    for r in renamed_taxa_cols["taxonomic_status"].unique():
        if r not in status_priority:
            raise ValueError(f'Rank priority list does not contain {r} and needs updating.')
    renamed_taxa_cols['taxonomic_status'] = pd.Categorical(renamed_taxa_cols['taxonomic_status'], status_priority)
    renamed_taxa_cols.sort_values('taxonomic_status', inplace=True)

    renamed_taxa_cols.drop_duplicates(subset=['taxon_name'], inplace=True, keep='first')

    cols_to_drop = [c for c in renamed_taxa_cols.columns if (c not in renaming.values() and c != 'taxon_name')]
    renamed_taxa_cols.drop(columns=cols_to_drop, inplace=True)

    # Merge in this way to preserve index from df
    merged_with_taxa = df.reset_index().merge(renamed_taxa_cols, left_on=name_col, right_on='taxon_name',
                                suffixes=(False, False)).set_index('index')

    return merged_with_taxa
