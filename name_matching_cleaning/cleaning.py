import re

import numpy as np
import pandas as pd
from typing import List

from numpy import isnan


def clean_ids(given_value: str) -> str:
    '''
    Strips urn:lsid:ipni.org:names: from id
    '''
    try:
        if re.search('urn:lsid:ipni.org:names:', given_value):
            pos = re.search('urn:lsid:ipni.org:names:', given_value).end()
            return given_value[pos:]
        else:
            return np.nan
    except TypeError:
        return given_value


def merge_columns(df: pd.DataFrame, new_col: str, old_columns: List[str]):
    '''
    Creates a new column using old columns by getting first non empty instance from the old columns
    :param df:
    :param new_col:
    :param old_columns:
    :return:
    '''
    # # Merge Accepted IDs
    df[new_col] = df[old_columns].agg(lambda x: next(y for y in x.values if not y==''), axis=1)
    df = df.drop(columns=old_columns)
    return df


def compile_hits(all_dfs: List[pd.DataFrame], output_csv: str):
    sources_cols = [c for c in all_dfs[0].columns.tolist() if 'Source' in c]
    snippet_cols = [c for c in all_dfs[0].columns.tolist() if 'Snippet' in c]
    cols_to_keep = ['Accepted_ID', 'Accepted_Name', 'Family', 'Rank'] + sources_cols + snippet_cols

    for df in all_dfs:
        cols_to_drop = [c for c in df.columns if
                        c not in cols_to_keep]
        df.drop(columns=cols_to_drop, inplace=True)

    merged_dfs = all_dfs[0]
    if len(all_dfs)>1:
        for i in all_dfs[1:]:
            merged_dfs = pd.merge(merged_dfs, i, on='Accepted_ID', how='outer')

        acc_cols = [c for c in merged_dfs.columns.tolist() if 'Accepted_Name' in c]
        merged_dfs = merge_columns(merged_dfs, 'Accepted_Name', acc_cols)

        rank_cols = [c for c in merged_dfs.columns.tolist() if 'Rank' in c]
        merged_dfs = merge_columns(merged_dfs, 'Rank', rank_cols)

        new_sources_cols = [c for c in merged_dfs.columns.tolist() if 'Source' in c]
        # Merge Sources:
        for col in new_sources_cols:
            merged_dfs[col] = merged_dfs[col].astype('string')
            merged_dfs[col] = merged_dfs[col].fillna('')
        merged_dfs['Sources'] = merged_dfs[new_sources_cols].agg(':'.join, axis=1)
        merged_dfs.drop(columns=new_sources_cols, inplace=True)

    start_cols = ['Accepted_Name', 'Accepted_ID']
    out_dfs = merged_dfs[[c for c in merged_dfs if c in start_cols]
                         + [c for c in merged_dfs if c not in start_cols]]

    out_dfs.to_csv(output_csv)
