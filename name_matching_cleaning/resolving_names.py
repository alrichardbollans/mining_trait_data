import pandas as pd

from name_matching_cleaning import get_wcvp_info_for_names_in_column

def resolve_unmatched(unmatched: pd.DataFrame, name_col: str) -> pd.DataFrame:
    """
    Trys to resolve matches by first checking taxa list and then relying on manual resolution
    :param unmatched:
    :return:
    """
    wcvp_matches = get_wcvp_info_for_names_in_column(unmatched, name_col)
    wcvp_matches.dropna(subset=['Accepted_Name'], inplace=True)
    if len(wcvp_matches.index) == len(unmatched.index):
        wcvp_matches[name_col] = wcvp_matches['Accepted_Name']
        return wcvp_matches
    else:
        _manually_resolve_missing_matches(unmatched)
        # raise ValueError('Unmatched not in wcvp')


def _manually_resolve_missing_matches(unmatched):
    print("TODO: To be implemented if errors are raised")
    print("WARNING: You have unresolved submissions. These can be manually addressed in the ")


def _get_resolutions_with_single_rank(df: pd.DataFrame, rank: str) -> pd.DataFrame:
    """
    Gets records for submissions which only match with the given rank and finds records where the accepted name
    is contained in the submission
    :param df:
    :param rank:
    :return:
    """
    submissions_with_rank = df[df['Accepted_Rank'] == rank]
    submissions_without_rank = df[df['Accepted_Rank'] != rank]

    # Submissions where ranks for all matches is the same
    submissions_with_single_rank = df[
        df['submitted'].isin(submissions_with_rank['submitted'].values) & ~df['submitted'].isin(
            submissions_without_rank['submitted'].values)]

    # Matches where accepted name is in submitted name
    submissions_with_single_rank_with_acc_name = submissions_with_single_rank[
        ~submissions_with_single_rank['Accepted_Name'].isna()]
    accepted_names_in_submitted_names = submissions_with_single_rank_with_acc_name[
        submissions_with_single_rank_with_acc_name.apply(lambda x: x['Accepted_Name'] in x['submitted'], axis=1)]

    return accepted_names_in_submitted_names