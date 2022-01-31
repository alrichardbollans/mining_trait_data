import pandas as pd
from typing import List

from name_matching_cleaning import get_wcvp_info_for_names_in_column
from taxa_lists import get_all_taxa


def resolve_missing_matches(unmatched_submissions_df: pd.DataFrame,
                            families_of_interest: List[str] = None) -> pd.DataFrame:
    """
    Manually resolve matches.
    :param name_col:
    :param unmatched_submissions_df:
    :return:
    """
    if len(unmatched_submissions_df.index) > 0:
        # For each submission, check if any accepted name is contained in the name, then take the lowest rank of match
        all_taxa = get_all_taxa(families_of_interest=families_of_interest, accepted=True)

        # TODO: fix this to get records in taxa list with name contained in submissions.
        accepted_name_containment = all_taxa[all_taxa['taxon_name'].str in
            '|'.join(unmatched_submissions_df['submitted'].values.tolist())]
        # accepted_name_containment = all_taxa[
        #     all_taxa.apply(lambda x: x['taxon_name'] in unmatched_submissions_df['submitted'], axis=1)]
        print(accepted_name_containment)

        # TODO: filter out higher ranking matches
        most_precise_match = accepted_name_containment
        most_precise_match.rename(columns={'taxon_name':'submitted'})

        matches = pd.merge(unmatched_submissions_df, most_precise_match, on='submitted', sort=False)
    else:
        return unmatched_submissions_df


def manual_resolution(unmatched_submissions_df: pd.DataFrame, name_col: str):
    if len(unmatched_submissions_df.index) > 0:
        print(f'Warning some submissions have not been resolved and must be manually resolved')
    else:
        return unmatched_submissions_df


def _get_resolutions_with_single_rank(submission_df_with_accepted_info: pd.DataFrame, rank: str) -> pd.DataFrame:
    """
    Gets records for submissions which only match with the given rank and finds records where the accepted name
    is contained in the submission
    :param submission_df_with_accepted_info:
    :param rank:
    :return:
    """
    submissions_with_rank = submission_df_with_accepted_info[submission_df_with_accepted_info['Accepted_Rank'] == rank]
    submissions_without_rank = submission_df_with_accepted_info[
        submission_df_with_accepted_info['Accepted_Rank'] != rank]

    # Submissions where ranks for all matches is the same
    submissions_with_single_rank = submission_df_with_accepted_info[
        submission_df_with_accepted_info['submitted'].isin(submissions_with_rank['submitted'].values) & ~
        submission_df_with_accepted_info['submitted'].isin(
            submissions_without_rank['submitted'].values)]

    # Matches where accepted name is in submitted name
    submissions_with_single_rank_with_acc_name = submissions_with_single_rank[
        ~submissions_with_single_rank['Accepted_Name'].isna()]
    accepted_names_in_submitted_names = submissions_with_single_rank_with_acc_name[
        submissions_with_single_rank_with_acc_name.apply(lambda x: x['Accepted_Name'] in x['submitted'], axis=1)]

    return accepted_names_in_submitted_names
