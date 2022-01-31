import hashlib
import os

import pandas as pd
from typing import List

from name_matching_cleaning import get_wcvp_info_for_names_in_column, \
    get_knms_name_matches, id_lookup_wcvp, resolve_missing_matches, clean_urn_ids
from name_matching_cleaning.resolving_names import _get_resolutions_with_single_rank

_temp_outputs_dir = 'name matching temp outputs'

from taxa_lists import get_all_taxa


def _get_knms_matches_and_accepted_info_from_names_in_column(df: pd.DataFrame, name_col: str,
                                                             families_of_interest: List[str] = None) -> pd.DataFrame:
    """
    Matches names in df using knms and gets corresponding accepted info from wcvp.
    :param df:
    :param name_col:
    :return:
    """
    match_records = get_knms_name_matches(df[name_col].values)

    single_matches = match_records[match_records['match_state'] == 'true'].copy()
    single_matches_with_info = get_accepted_info_from_ids_in_column(single_matches, 'ipni_id',
                                                                    families_of_interest=families_of_interest)

    multiple_matches = match_records[match_records['match_state'] == 'multiple_matches'].copy()
    best_matches = _find_best_matches_from_multiples(multiple_matches)

    initial_matches = pd.concat([single_matches_with_info, best_matches], axis=0)

    unmatched = match_records[~match_records['submitted'].isin(initial_matches['submitted'].values)]
    unmatched_resolutions = resolve_missing_matches(unmatched, families_of_interest=families_of_interest)

    resolved_df = pd.concat([single_matches_with_info, best_matches, unmatched_resolutions], axis=0)
    resolved_df.rename(columns={'submitted': name_col}, inplace=True)

    resolved_df.drop(columns=['match_state', 'ipni_id', 'matched_name'], inplace=True)

    merged_df = pd.merge(df, resolved_df, on=name_col, sort=False)

    return merged_df


def _find_best_matches_from_multiples(multiple_match_records: pd.DataFrame, families_of_interest=None) -> pd.DataFrame:
    """
    Gets best matching record for each set of multiple matches, and returns a dataframe of single matches
    :param multiple_match_records:
    :param families_of_interest:
    :return:
    """
    # First find accepted info for the multiple matches
    multiple_match_records['ipni_id'] = multiple_match_records['ipni_id'].apply(clean_urn_ids)
    multiple_matches_with_accepted_ids = get_accepted_info_from_ids_in_column(multiple_match_records,
                                                                              'ipni_id',
                                                                              families_of_interest=families_of_interest)

    # Matches where accepted name is the same as the submitted name
    accepted_names_matching_submitted_names = multiple_matches_with_accepted_ids[
        multiple_matches_with_accepted_ids['submitted'] == multiple_matches_with_accepted_ids['Accepted_Name']]

    # Only need to consider matches where submission differs or submission is the same and accepted ids differ
    unique_matches = multiple_matches_with_accepted_ids.drop_duplicates(
        subset=['submitted', 'Accepted_ID'], keep='first')

    # Matches where the submitted name has a unique accepted match
    submitted_names_with_single_accepted_match = unique_matches.drop_duplicates(subset=['submitted'], keep=False)

    unresolved_submissions = unique_matches[
        ~unique_matches["submitted"].isin(submitted_names_with_single_accepted_match["submitted"])]
    # We only check submissions where ranks are the same for every submission match
    # Otherwise a subspecies may match with it's parent and be erroneously resolved to that
    ranks = list(unresolved_submissions['Accepted_Rank'].unique())
    accepted_name_in_submitted_names = []
    # Matches where ranks are the same rank
    for r in ranks:
        r_matches = _get_resolutions_with_single_rank(unresolved_submissions, r)
        accepted_name_in_submitted_names.append(r_matches)

    matches_to_use = pd.concat([accepted_names_matching_submitted_names,
                                submitted_names_with_single_accepted_match] + accepted_name_in_submitted_names)
    matches_to_use.drop_duplicates(subset=['submitted'], keep='first', inplace=True)

    unmatched_df = multiple_matches_with_accepted_ids[
        ~multiple_matches_with_accepted_ids['submitted'].isin(matches_to_use['submitted'].values)]
    if len(unmatched_df.index) > 0:
        df_str = unmatched_df.to_string()
        str_to_hash = str(df_str).encode()
        temp_basename_csv = str(hashlib.md5(str_to_hash).hexdigest()) + ".csv"
        try:
            os.mkdir(_temp_outputs_dir)
        except FileExistsError as error:
            pass
        outfile = os.path.join(_temp_outputs_dir, 'unmatched_samples_with_multiple_knms_hits' + temp_basename_csv)
        print(
            f'Warning: Some samples have multiple matches in knms but havent been automatically resolved. Note that these may still be resolved in unmatched resolving. See {outfile}.{unmatched_df}')
        unmatched_df.to_csv(outfile)
    return matches_to_use


def get_accepted_info_from_ids_in_column(df: pd.DataFrame, id_col_name: str,
                                         families_of_interest: List[str] = None) -> pd.DataFrame:
    """
    Appends accepted info columns to df from list of taxa, based on ids in id_col_name
    :param all_taxa:
    :param df:
    :param id_col_name:
    :return:
    """

    all_taxa = get_all_taxa(families_of_interest=families_of_interest)
    dict_of_values = {'Accepted_Name': [], 'Accepted_ID': [], 'Accepted_Rank': [],
                      'Accepted_Species': [], 'Accepted_Species_ID': []}
    for x in df[id_col_name].values:
        acc_info = id_lookup_wcvp(all_taxa, x)
        for k in dict_of_values:
            dict_of_values[k].append(acc_info[k])

    match_df = pd.DataFrame(dict_of_values)

    if len(match_df.index) != len(df.index):
        raise ValueError('Generating accepted info is mismatched')

    # Set indices for concatenating properly
    match_df.set_index(df.index, inplace=True)
    return pd.concat([df, match_df], axis=1)


def get_accepted_info_from_names_in_column(df: pd.DataFrame, name_col: str, families_of_interest: List[str] = None,
                                           keep_unmatched=True):
    """
    First tries to match names in df to wcvp directly to obtain accepted info and then
    matches names in df using knms and gets corresponding accepted info from wcvp
    :param df:
    :param name_col:
    :param all_taxa:
    :return:
    """
    all_taxa = get_all_taxa(families_of_interest=families_of_interest)
    duplicateRows = df[df.duplicated()]
    if len(duplicateRows.index) > 0:
        print(f'Warning: duplicated rows exist is data and may be merged.')
        print(duplicateRows)
    na_rows = df[df[name_col].isna()]
    if len(na_rows.index) > 0:
        print(f'Warning: Rows in {name_col} with nan values. {na_rows}')
        df.dropna(subset=[name_col], inplace=True)

    # First match with exact matches in wcvp
    name_match_df = get_wcvp_info_for_names_in_column(df, name_col, all_taxa=all_taxa)
    wcvp_matches = name_match_df[~name_match_df['Accepted_Name'].isna()]

    # If exact matches aren't found in wcvp, use knms first
    unmatched_name_df = df[name_match_df['Accepted_Name'].isna()]

    matches_with_knms = _get_knms_matches_and_accepted_info_from_names_in_column(unmatched_name_df, name_col,
                                                                                 families_of_interest=families_of_interest)
    resolved_df = pd.concat([wcvp_matches, matches_with_knms], axis=0)

    # Provide temp outputs
    unmatched_final_df = df[~df[name_col].isin(resolved_df[name_col].values)]
    if len(unmatched_final_df.index) > 0:

        df_str = unmatched_final_df.to_string()
        str_to_hash = str(df_str).encode()
        temp_basename_csv = str(hashlib.md5(str_to_hash).hexdigest()) + ".csv"
        try:
            os.mkdir(_temp_outputs_dir)
        except FileExistsError as error:
            pass
        outfile = os.path.join(_temp_outputs_dir, 'unmatched_samples' + temp_basename_csv)
        print(f'Warning: Unmatched samples. Check {outfile}.{unmatched_final_df}')
        unmatched_final_df.to_csv(outfile)

        # TODO: append unmatched to resolved
        if keep_unmatched:
            resolved_df = pd.concat([resolved_df, unmatched_final_df])

    return resolved_df


if __name__ == '__main__':
    taxa = get_all_taxa()
    sarc = taxa[taxa['genus'] == 'Sarcorhiza']
    sarc.to_csv('test.csv')
