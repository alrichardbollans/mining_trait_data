import os
from typing import List

import pandas as pd

COL_NAMES = {'acc_name': 'Accepted_Name',
             'acc_species': 'Accepted_Species',
             'acc_species_id': 'Accepted_Species_ID',
             'acc_id': 'Accepted_ID',
             'acc_rank': 'Accepted_Rank',
             'single_source': 'Source',
             'sources': 'Compiled_Sources'}


def filter_out_ranks(df: pd.DataFrame) -> pd.DataFrame:
    ranks_of_interest = ['Species']

    return df[df[COL_NAMES['acc_rank']].isin(ranks_of_interest)]


def generate_temp_output_file_paths(filetag: str, temp_output_path: str):
    # Temp outputs
    temp_output_cleaned_csv = os.path.join(temp_output_path, filetag + '_cleaned.csv')
    temp_output_accepted_csv = os.path.join(temp_output_path, filetag + '_accepted.csv')

    return temp_output_cleaned_csv, temp_output_accepted_csv


def _merge_columns(df: pd.DataFrame, new_col: str, old_columns: List[str]):
    '''
    Creates a new column using old columns by getting first non empty instance from the old columns
    :param df:
    :param new_col:
    :param old_columns:
    :return:
    '''
    if len(old_columns) > 1:
        for col in old_columns:
            df[col] = df[col].astype(str)
        df[new_col] = df[old_columns].agg(lambda x: next((y for y in x.values if (y != '' and y != 'nan')), 'nan'),
                                          axis=1)
        df = df.drop(columns=old_columns)
    return df


def _merge_on_accepted_id(x: pd.DataFrame, y: pd.DataFrame) -> pd.DataFrame:
    merged_dfs = pd.merge(x, y, on=COL_NAMES['acc_id'], how='outer')
    merged_dfs[COL_NAMES['sources']] = merged_dfs[COL_NAMES['sources']].apply(
        lambda d: d if isinstance(d, list) else [])

    new_sources_cols = [c for c in merged_dfs.columns.tolist() if
                        (COL_NAMES['single_source'].lower() in c.lower() and c != COL_NAMES[
                            'sources'] and c != 'dummy_new_sources')]
    # # Merge Sources:
    for col in new_sources_cols:
        merged_dfs[col] = merged_dfs[col].fillna('')
    x = merged_dfs[COL_NAMES['sources']].values.tolist()
    merged_dfs['dummy_new_sources'] = merged_dfs[new_sources_cols].values.tolist()

    merged_dfs[COL_NAMES['sources']] = merged_dfs[COL_NAMES['sources']] + merged_dfs['dummy_new_sources']
    merged_dfs.drop(columns=['dummy_new_sources'], inplace=True)

    # Remove empty sources
    def rmv_empty_sources(given_sources_str: List):
        source_list = list(given_sources_str)
        if '' in source_list:
            source_list.remove('')

        return source_list

    merged_dfs[COL_NAMES['sources']] = merged_dfs[COL_NAMES['sources']].apply(rmv_empty_sources)

    source_cols_to_drop = [c for c in new_sources_cols if c != COL_NAMES['sources']]
    merged_dfs.drop(columns=source_cols_to_drop, inplace=True)

    acc_cols = [c for c in merged_dfs.columns.tolist() if COL_NAMES['acc_name'] in c]
    merged_dfs = _merge_columns(merged_dfs, COL_NAMES['acc_name'], acc_cols)

    acc_sp_id_cols = [c for c in merged_dfs.columns.tolist() if COL_NAMES['acc_species_id'] in c]
    acc_sp_cols = [c for c in merged_dfs.columns.tolist() if (COL_NAMES['acc_species'] in c and '_ID' not in c)]
    merged_dfs = _merge_columns(merged_dfs, COL_NAMES['acc_species'], acc_sp_cols)

    merged_dfs = _merge_columns(merged_dfs, COL_NAMES['acc_species_id'], acc_sp_id_cols)

    rank_cols = [c for c in merged_dfs.columns.tolist() if COL_NAMES['acc_rank'] in c]
    merged_dfs = _merge_columns(merged_dfs, COL_NAMES['acc_rank'], rank_cols)

    return merged_dfs


def _merge_snippets_of_repeated_taxa(df: pd.DataFrame):
    snippet_cols = [c for c in df.columns.tolist() if 'snippet' in c.lower()]
    if len(snippet_cols) > 1:
        print(f'Warning appears to be more than one snippet column in: {df}')
    if len(snippet_cols) < 1:
        return df
    if len(df[df[COL_NAMES['acc_id']].duplicated()]) > 0:
        for snip_col in snippet_cols:
            print(f'Warning: Repeated taxa in:')
            print(df)
            print('Resolving snippets')

            compiled = df.groupby([COL_NAMES['acc_id']])[snip_col].apply(','.join).reset_index()
            merged = pd.merge(compiled, df.drop(columns=snip_col), on=[COL_NAMES['acc_id']], )
            merged.drop_duplicates(subset=[COL_NAMES['acc_id']], inplace=True)

            merged = merged[df.columns.tolist()]

            # Remove empty sources
            def rmv_duplicates_reorder(given_sources_str: str):
                source_list = given_sources_str.split(',')
                out_list = []
                for s in source_list:
                    if s not in out_list:
                        out_list.append(s)

                out_list = ','.join(sorted(out_list))
                return out_list

            merged[snip_col] =merged[snip_col].apply(rmv_duplicates_reorder)

        return merged
    else:
        return df


def compile_hits(all_dfs: List[pd.DataFrame], output_csv: str):
    '''
    Dataframes should contain the following headings 'Source', '[sourcename]_snippet', 'Accepted_Name',
    'Accepted_Species', 'Accepted_Rank' and 'Accepted_ID'
    :param all_dfs: List of dataframes to merge together
    :param output_csv: Output file
    :return:
    '''
    # First remove extraneous columns
    sources_cols = []
    snippet_cols = []
    for df in all_dfs:
        [sources_cols.append(c) for c in df.columns.tolist() if 'source' in c.lower()]
        [snippet_cols.append(c) for c in df.columns.tolist() if 'snippet' in c.lower()]
    cols_to_keep = list(COL_NAMES.values()) + sources_cols + snippet_cols

    # Do some cleaning
    cleaned_dfs = []
    for df in all_dfs:
        cols_to_drop = [c for c in df.columns if
                        c not in cols_to_keep]
        df = df.drop(columns=cols_to_drop)
        df = df.dropna(subset=[COL_NAMES['acc_name']])
        df = _merge_snippets_of_repeated_taxa(df)
        cleaned_dfs.append(df)

    # Do merges
    merged_dfs = cleaned_dfs[0].copy()

    merged_dfs[COL_NAMES['sources']] = merged_dfs[[COL_NAMES['single_source']]].values.tolist()

    merged_dfs = merged_dfs.drop(columns=[COL_NAMES['single_source']])

    if len(cleaned_dfs) > 1:
        for i in cleaned_dfs[1:]:
            merged_dfs = _merge_on_accepted_id(merged_dfs, i)
    # Put name columns at begining
    start_cols = [COL_NAMES['acc_name'], COL_NAMES['acc_id'], COL_NAMES['acc_rank'], COL_NAMES['acc_species'],
                  COL_NAMES['acc_species_id']]
    out_dfs = merged_dfs[[c for c in merged_dfs if c in start_cols]
                         + [c for c in merged_dfs if c not in start_cols]]
    # And source column at the end
    out_dfs = out_dfs[[c for c in out_dfs if c != COL_NAMES['sources']]
                      + [COL_NAMES['sources']]]

    out_dfs.drop_duplicates(subset=[COL_NAMES['acc_id']] + snippet_cols, inplace=True)

    out_dfs.to_csv(output_csv)
