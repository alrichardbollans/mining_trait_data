import hashlib
import os

import numpy as np
import pandas as pd
from typing import List

from pkg_resources import resource_filename

from name_matching_cleaning import get_wcvp_info_for_names_in_column, \
    get_knms_name_matches, id_lookup_wcvp, clean_urn_ids, COL_NAMES, remove_whitespace, temp_outputs_dir
from name_matching_cleaning.resolving_names import _get_resolutions_with_single_rank

from taxa_lists import get_all_taxa

matching_data_path = resource_filename(__name__, 'matching data')
_resolution_csv = os.path.join(matching_data_path, 'manual_match.csv')


def _temp_output(df: pd.DataFrame, tag: str, warning: str):
    df_str = df.to_string()
    str_to_hash = str(df_str).encode()
    temp_basename_csv = str(hashlib.md5(str_to_hash).hexdigest()) + ".csv"
    try:
        os.mkdir(temp_outputs_dir)
    except FileExistsError as error:
        pass
    outfile = os.path.join(temp_outputs_dir, tag + temp_basename_csv)
    print(f'{warning}. Check tempfile: {outfile}.')
    df.to_csv(outfile)


def _capitalize_first_letter_of_taxon(g: str, check_string_is_uppercase=False):
    try:
        if check_string_is_uppercase:
            if not g.isupper():
                return g

        append_to_beginning = ''
        if g.startswith('× '):
            append_to_beginning = '× '
            g = g[2:]
        l = g.lower()

        if len([x for x in g if x == " "]) > 1:
            # KNMS does not return matches where authors are incorrectly capitalised
            return g

        return append_to_beginning + l.capitalize()
    except AttributeError:
        return g


def _autoresolve_missing_matches(unmatched_submissions_df: pd.DataFrame, name_col: str,
                                 families_of_interest: List[str] = None) -> pd.DataFrame:
    """
    Manually resolve matches.
    :param unmatched_submissions_df:
    :return:
    """
    if len(unmatched_submissions_df.index) > 0:
        _temp_output(unmatched_submissions_df, 'unmatched_to_autoresolve',
                     "Resolving submitted names which weren't initially matched using KNMS. This may take some time... This can be sped up by specifying families of interest (if you haven't already done so) or checking the temp file for misspelled submissions.")

        # For each submission, check if any accepted name is contained in the name, then take the lowest rank of match
        all_taxa = get_all_taxa(families_of_interest=families_of_interest, accepted=True)

        # Get more precise list of taxa which possibly matches submissions
        accepted_name_containment = all_taxa[
            all_taxa.apply(lambda x: any(x['taxon_name'] in y for y in unmatched_submissions_df[name_col].values),
                           axis=1)]

        # Create a dataframe of submissions with possible matches
        dict_for_matches = {name_col: [], 'Accepted_Name': [], 'Accepted_ID': [], 'Accepted_Rank': [],
                            'Accepted_Species': [], 'Accepted_Species_ID': [], 'taxonomic_status_of_submitted_name': []}
        for s in unmatched_submissions_df[name_col].values:
            for taxa in accepted_name_containment['taxon_name']:
                if taxa in s:
                    dict_for_matches[name_col].append(s)
                    acc_id = \
                        accepted_name_containment.loc[accepted_name_containment['taxon_name'] == taxa, 'kew_id'].iloc[
                            0]
                    dict_for_record = id_lookup_wcvp(accepted_name_containment, acc_id)

                    for k in dict_for_record:
                        dict_for_matches[k].append(dict_for_record[k])

        match_df = pd.DataFrame(dict_for_matches)

        # Order the dataframe by rank
        rank_priority = ["Subspecies", "Variety", "Species", "Genus"]
        for r in match_df["Accepted_Rank"].unique():
            if r not in rank_priority:
                raise ValueError(f'Rank priority list does not contain {r} and needs updating.')
        match_df['Accepted_Rank'] = pd.Categorical(match_df['Accepted_Rank'], rank_priority)
        match_df.sort_values('Accepted_Rank', inplace=True)

        # Remove genera matches where submitted name has more than one word.
        # This to avoid matching mispelt species to genera
        # This is a problem for hybrid genera but these need resolving differently anyway.
        if len(match_df.index) > 0:
            match_df = match_df[~((match_df['Accepted_Rank'] == 'Genus') & match_df[name_col].str.contains(" "))]

        # Get the most precise match by dropping duplicate submissions
        most_precise_match = match_df.drop_duplicates(subset=[name_col], keep='first')

        # Merge with original data
        matches = pd.merge(unmatched_submissions_df, most_precise_match, on=name_col, sort=False)
        matches = matches.dropna(subset=['Accepted_Name'])
        return matches
    else:
        return unmatched_submissions_df


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

    resolved_df = pd.concat([single_matches_with_info, best_matches], axis=0)
    resolved_df.rename(columns={'submitted': name_col}, inplace=True)

    resolved_df.drop(columns=['match_state', 'ipni_id', 'matched_name'], inplace=True)

    # This trick allows merging on columns with duplicates and matches duplicates rather than repeating them
    df['cc'] = df.groupby(name_col).cumcount()
    resolved_df['cc'] = resolved_df.groupby(name_col).cumcount()
    merged_df = df.merge(resolved_df, how='outer').drop(columns='cc', axis=1)
    merged_df = merged_df.dropna(subset=['Accepted_Name'])
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
        _temp_output(unmatched_df, 'unmatched_samples_with_multiple_knms_hits',
                     'Warning: Some samples have multiple matches in knms but havent been automatically resolved. Note that these may still be resolved in unmatched resolving')

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

    concat_df = pd.concat([df, match_df], axis=1)

    return concat_df


def get_accepted_info_from_names_in_column(in_df: pd.DataFrame, name_col: str, families_of_interest: List[str] = None):
    """
    First tries to match names in df to wcvp directly to obtain accepted info and then
    matches names in df using knms and gets corresponding accepted info from wcvp
    :param df:
    :param name_col:
    :param all_taxa:
    :return:
    """

    df = in_df.copy()
    df = df.drop_duplicates(subset=[name_col])

    na_rows = df[df[name_col].isna()]
    if len(na_rows.index) > 0:
        print(f'Warning: Rows in {name_col} with nan values. {na_rows}')
        df.dropna(subset=[name_col], inplace=True)

    # Standardise input names
    # Non standard captialisation causes issues
    # If input names are all caps then we change to capitalise the first letter
    df[name_col] = df[name_col].apply(_capitalize_first_letter_of_taxon, check_string_is_uppercase=True)
    df[name_col] = df[name_col].apply(remove_whitespace)

    # First get manual matches
    manual_match_df = pd.read_csv(_resolution_csv)
    manual_match_df = manual_match_df[manual_match_df['submitted'].isin(df[name_col].values.tolist())]
    man_matches_with_accepted_info = get_accepted_info_from_ids_in_column(manual_match_df, 'resolution_id')
    man_matches_with_accepted_info = man_matches_with_accepted_info.dropna(subset=['Accepted_Name'])
    manual_matches = pd.merge(df, man_matches_with_accepted_info, left_on=name_col, right_on='submitted', sort=False)
    unmatched_manual_df = df[~df[name_col].isin(manual_matches[name_col].values)]

    # Then match with exact matches in wcvp
    all_taxa = get_all_taxa(families_of_interest=families_of_interest)
    wcvp_exact_name_match_df = get_wcvp_info_for_names_in_column(unmatched_manual_df, name_col, all_taxa=all_taxa)
    wcvp_manual_resolved_df = pd.concat([wcvp_exact_name_match_df, manual_matches], axis=0)
    unmatched_name_df = df[~df[name_col].isin(wcvp_manual_resolved_df[name_col].values)]

    # If exact matches aren't found in wcvp, use knms
    matches_with_knms = _get_knms_matches_and_accepted_info_from_names_in_column(unmatched_name_df, name_col,
                                                                                 families_of_interest=families_of_interest)
    wcvp_manual_knms_resolved_df = pd.concat([wcvp_manual_resolved_df, matches_with_knms], axis=0)
    unmatched_df = df[~df[name_col].isin(wcvp_manual_knms_resolved_df[name_col].values)]

    # Get autoresolved matches
    unmatched_resolutions = _autoresolve_missing_matches(unmatched_df, name_col,
                                                         families_of_interest=families_of_interest)

    final_resolved_df = pd.concat([unmatched_resolutions, wcvp_manual_knms_resolved_df], axis=0)

    # Provide temp outputs
    unmatched_final_df = df[~df[name_col].isin(final_resolved_df[name_col].values)]
    if len(unmatched_final_df.index) > 0:
        _temp_output(unmatched_final_df, 'unmatched_samples',
                     'WARNING: some submissions have not been resolved and must be manually resolved. Consider fixing names in your original data.')
        final_resolved_df = pd.concat([final_resolved_df, unmatched_final_df])
    cols_to_drop = [c for c in final_resolved_df.columns.tolist() if
                    (c not in df.columns.tolist() and c not in list(COL_NAMES.values()))]
    final_resolved_df.drop(columns=cols_to_drop, inplace=True)

    def get_acc_info_from_matches(submitted_name: str, col: str):
        return final_resolved_df[final_resolved_df[name_col] == submitted_name][col].values[0]

    out_df = df.copy()
    for k in COL_NAMES:
        if k not in ['single_source', 'sources']:
            out_df[COL_NAMES[k]] = out_df[name_col]
            out_df[COL_NAMES[k]] = out_df[COL_NAMES[k]].apply(get_acc_info_from_matches, col=COL_NAMES[k])

    return out_df


if __name__ == '__main__':
    taxa = get_all_taxa()
    sarc = taxa[taxa['genus'] == 'Sarcorhiza']
    sarc.to_csv('test.csv')
