import pandas as pd

from name_matching_cleaning import clean_urn_ids, get_wcvp_info_for_names_in_column, \
    get_accepted_info_from_ids_in_column, get_knms_name_matches

from taxa_lists import get_all_taxa


def _find_best_matches_from_multiples(multiple_match_records: pd.DataFrame, families_of_interest=None) -> pd.DataFrame:
    """
    Gets best matching record for each set of multiple matches, and returns a dataframe of single matches
    :param multiple_match_records:
    :param families_of_interest:
    :return:
    """
    wcvp_taxa = get_all_taxa(families_of_interest=families_of_interest)
    multiple_match_records['ipni_id'] = multiple_match_records['ipni_id'].apply(clean_urn_ids)
    multiple_matches_with_accepted_ids = get_accepted_info_from_ids_in_column(multiple_match_records,
                                                                              'ipni_id', all_taxa=wcvp_taxa)

    # Matches where accepted name is the same as the submitted name
    accepted_names_matching_submitted_names = multiple_matches_with_accepted_ids[
        multiple_matches_with_accepted_ids['submitted'] == multiple_matches_with_accepted_ids['Accepted_Name']]

    # Matches where submission differs or submission is the same and accepted ids differ
    unique_matches = multiple_matches_with_accepted_ids.drop_duplicates(
        subset=['submitted', 'Accepted_ID'], keep='first')

    # Matches where the submitted name has a unique accepted match
    submitted_names_with_single_accepted_match = unique_matches.drop_duplicates(subset=['submitted'], keep=False)

    matches_to_use = pd.concat([accepted_names_matching_submitted_names, submitted_names_with_single_accepted_match])
    matches_to_use.drop_duplicates(subset=['submitted'], keep='first', inplace=True)

    return matches_to_use


def _manually_resolve_missing_matches():
    # TODO: To be implemented if errors are raised
    pass


def _resolve_unmatched(unmatched: pd.DataFrame) -> pd.DataFrame:
    """
    Trys to resolve matches by first checking taxa list and then relying on manual resolution
    :param unmatched:
    :return:
    """
    wcvp_matches = get_wcvp_info_for_names_in_column(unmatched, 'submitted')
    if len(wcvp_matches.index) == len(unmatched.index):
        wcvp_matches['submitted'] = wcvp_matches['Accepted_Name']
        return wcvp_matches
    else:
        _manually_resolve_missing_matches()
        raise ValueError('Unmatched not in wcvp')


def _get_knms_matches_and_accepted_info_from_names_in_column(df: pd.DataFrame, name_col: str) -> pd.DataFrame:
    """
    Matches names in df using knms and gets corresponding accepted info from wcvp.
    :param df:
    :param name_col:
    :return:
    """
    match_records = get_knms_name_matches(df[name_col].values)

    single_matches = match_records[match_records['match_state'] == 'true'].copy()
    single_matches_with_info = get_accepted_info_from_ids_in_column(single_matches, 'ipni_id')

    multiple_matches = match_records[match_records['match_state'] == 'multiple_matches'].copy()
    best_matches = _find_best_matches_from_multiples(multiple_matches)

    unmatched = match_records[match_records['match_state'] == 'false'].copy()
    unmatched_resolutions = _resolve_unmatched(unmatched)

    resolved_df = pd.concat([single_matches_with_info, best_matches, unmatched_resolutions], axis=0)
    resolved_df.rename(columns={'submitted': name_col}, inplace=True)

    resolved_df.drop(columns=['match_state', 'ipni_id', 'matched_name'], inplace=True)

    merged_df = pd.merge(df, resolved_df, on=name_col, sort=False)

    return merged_df


def get_accepted_info_from_names_in_column(df: pd.DataFrame, name_col: str, all_taxa: pd.DataFrame = None):
    """
    First tries to match names in df to wcvp directly to obtain accepted info and then
    matches names in df using knms and gets corresponding accepted info from wcvp
    :param df:
    :param name_col:
    :param all_taxa:
    :return:
    """
    df.dropna(subset=[name_col], inplace=True)
    name_match_df = get_wcvp_info_for_names_in_column(df, name_col, all_taxa=all_taxa)
    wcvp_matches = name_match_df[~name_match_df['Accepted_Name'].isna()]

    unmatched_name_df = df[name_match_df['Accepted_Name'].isna()]

    matches_with_knms = _get_knms_matches_and_accepted_info_from_names_in_column(unmatched_name_df, name_col)
    resolved_df = pd.concat([wcvp_matches, matches_with_knms], axis=0)

    return resolved_df


if __name__ == '__main__':
    pass
