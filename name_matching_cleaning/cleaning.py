import os
import re

import numpy as np
import pandas as pd
from typing import List

col_names = {'acc_name': 'Accepted_Name',
             'acc_species': 'Accepted_Species',
             'acc_id': 'Accepted_ID',
             'acc_rank': 'Accepted_Rank',
             'single_source': 'Source',
             'sources': 'Sources'}


def filter_out_ranks(df: pd.DataFrame) -> pd.DataFrame:
    ranks_of_interest = ['Species']

    return df[df[col_names['acc_rank']].isin(ranks_of_interest)]


def generate_temp_output_file_paths(filetag: str, temp_output_path: str):
    # Temp outputs
    temp_output_cleaned_csv = os.path.join(temp_output_path, filetag + '_cleaned.csv')
    temp_output_accepted_csv = os.path.join(temp_output_path, filetag + '_accepted.csv')

    return temp_output_cleaned_csv, temp_output_accepted_csv


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
    for col in old_columns:
        df[col] = df[col].astype(str)
    df[new_col] = df[old_columns].agg(lambda x: next((y for y in x.values if (y != '' and y != 'nan')), 'nan'), axis=1)
    df = df.drop(columns=old_columns)
    return df


def merge_on_accepted_id(x: pd.DataFrame, y: pd.DataFrame) -> pd.DataFrame:

    merged_dfs = pd.merge(x, y, on=col_names['acc_id'], how='outer')

    new_sources_cols = [c for c in merged_dfs.columns.tolist() if (col_names['single_source'] in c)]
    # # Merge Sources:
    for col in new_sources_cols:
        merged_dfs[col] = merged_dfs[col].astype('string')
        merged_dfs[col] = merged_dfs[col].fillna('')
    merged_dfs[col_names['sources']] = merged_dfs[new_sources_cols].agg(':'.join, axis=1)
    source_cols_to_drop = [c for c in new_sources_cols if c != col_names['sources']]
    merged_dfs.drop(columns=source_cols_to_drop, inplace=True)

    acc_cols = [c for c in merged_dfs.columns.tolist() if col_names['acc_name'] in c]
    merged_dfs = merge_columns(merged_dfs, col_names['acc_name'], acc_cols)

    acc_sp_cols = [c for c in merged_dfs.columns.tolist() if col_names['acc_species'] in c]
    merged_dfs = merge_columns(merged_dfs, col_names['acc_species'], acc_sp_cols)

    rank_cols = [c for c in merged_dfs.columns.tolist() if col_names['acc_rank'] in c]
    merged_dfs = merge_columns(merged_dfs, col_names['acc_rank'], rank_cols)



    return merged_dfs


def compile_hits(all_dfs: List[pd.DataFrame], output_csv: str):
    # First remove extraneous columns
    sources_cols = []
    snippet_cols = []
    for df in all_dfs:
        [sources_cols.append(c) for c in df.columns.tolist() if 'Source' in c]
        [snippet_cols.append(c) for c in df.columns.tolist() if 'Snippet' in c]
    cols_to_keep = list(col_names.values()) + sources_cols + snippet_cols

    # Do some cleaning
    for df in all_dfs:
        cols_to_drop = [c for c in df.columns if
                        c not in cols_to_keep]
        df.drop(columns=cols_to_drop, inplace=True)
        df.dropna(subset={col_names['acc_name']}, inplace=True)

    # Do merges
    merged_dfs = all_dfs[0]
    merged_dfs[col_names['sources']] = merged_dfs[col_names['single_source']]
    merged_dfs.drop(columns=[col_names['single_source']], inplace=True)

    if len(all_dfs) > 1:
        for i in all_dfs[1:]:

            merged_dfs = merge_on_accepted_id(merged_dfs, i)



    start_cols = [col_names['acc_name'], col_names['acc_id'], col_names['acc_species'],col_names['acc_rank']]
    out_dfs = merged_dfs[[c for c in merged_dfs if c in start_cols]
                         + [c for c in merged_dfs if c not in start_cols]]
    out_dfs = out_dfs[[c for c in out_dfs if c != col_names['sources']]
                         + [col_names['sources']]]

    out_dfs.drop_duplicates(inplace=True)

    out_dfs.to_csv(output_csv)
