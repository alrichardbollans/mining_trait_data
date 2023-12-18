import os
from typing import List

import pandas as pd

single_source_col = 'Source'
compiled_sources_col = 'Compiled_Sources'


def _aggregate_data_on_accepted_names(in_df: pd.DataFrame) -> pd.DataFrame:
    from wcvp_download import wcvp_accepted_columns

    def _unique_sources(iterable):
        out = list(set(iterable))
        out.sort()
        return out

    grouped = in_df.groupby(wcvp_accepted_columns['name_w_author'])[single_source_col].apply(
        _unique_sources).reset_index(
        name=single_source_col)
    df = pd.merge(in_df.drop(columns=[single_source_col]), grouped, how='left',
                  on=wcvp_accepted_columns['name_w_author'])
    df = df.rename(columns={single_source_col: compiled_sources_col})

    df = df.drop_duplicates(subset=[wcvp_accepted_columns['name_w_author']])

    return df


def compile_hits(all_dfs: List[pd.DataFrame], output_csv: str) -> pd.DataFrame:
    '''
    Dataframes should contain the following headings 'Source', '[sourcename]_snippet', 'Accepted_Name',
    'Accepted_Species', 'Accepted_Rank' and 'Accepted_ID'
    :param all_dfs: List of dataframes to merge together
    :param output_csv: Output file
    :return:
    '''
    from wcvp_download import wcvp_accepted_columns

    OUTPUT_COL_NAMES = [wcvp_accepted_columns['name'], wcvp_accepted_columns['name_w_author'],
                        wcvp_accepted_columns['ipni_id'],
                        wcvp_accepted_columns['rank'],
                        wcvp_accepted_columns['species'],
                        wcvp_accepted_columns['species_w_author'],
                        wcvp_accepted_columns['species_ipni_id'],
                        wcvp_accepted_columns['family'],
                        compiled_sources_col]
    # Put name columns at begining
    start_cols = OUTPUT_COL_NAMES[:]
    start_cols.remove(compiled_sources_col)

    if len(all_dfs) == 0 or all(len(x.index) == 0 for x in all_dfs):
        out_dfs = pd.DataFrame(columns=start_cols + [compiled_sources_col])
        out_dfs.to_csv(output_csv)

        return out_dfs

    # First remove extraneous columns
    sources_cols = []
    snippet_cols = []
    for df in all_dfs:
        [sources_cols.append(c) for c in df.columns.tolist() if 'source' in c.lower()]
        [snippet_cols.append(c) for c in df.columns.tolist() if 'snippet' in c.lower()]
    cols_to_keep = OUTPUT_COL_NAMES + sources_cols

    # Do some cleaning
    cleaned_dfs = []
    for df in all_dfs:
        if single_source_col not in df.columns:
            raise ValueError(f'No source given in dataframe: {df}')
        cols_to_drop = [c for c in df.columns if
                        c not in cols_to_keep]
        df = df.drop(columns=cols_to_drop)
        df = df.dropna(subset=[wcvp_accepted_columns['name_w_author']])

        # Remove repeated entries across dataframes
        sources = []
        for clean_df in cleaned_dfs:
            for s in clean_df[single_source_col].unique().tolist():
                if s not in sources:
                    sources.append(s)

            df = pd.merge(df, clean_df[[wcvp_accepted_columns['name_w_author'], single_source_col]],
                          on=[wcvp_accepted_columns['name_w_author'], single_source_col], how="outer",
                          indicator=True)
            df = df.loc[df["_merge"] == "left_only"].drop("_merge", axis=1)

        if len(df) > 0:
            cleaned_dfs.append(df)

    concatted_dfs = pd.concat(cleaned_dfs)
    outdfs = _aggregate_data_on_accepted_names(concatted_dfs)

    out_dfs = outdfs[[c for c in start_cols if c in outdfs]
                     + [c for c in outdfs if c not in start_cols]]
    # And source column at the end
    out_dfs = out_dfs[[c for c in out_dfs if c != compiled_sources_col]
                      + [compiled_sources_col]]

    out_dfs = out_dfs.sort_values(by=wcvp_accepted_columns['name']).reset_index(drop=True)

    duplicate_hits_output = os.path.join(os.path.dirname(output_csv), 'duplicate_hits.csv')
    dup_hits_df = out_dfs[out_dfs.duplicated(subset=[wcvp_accepted_columns['name_w_author']], keep=False)]
    if len(dup_hits_df) > 0:
        dup_hits_df.to_csv(duplicate_hits_output)
        raise ValueError(
            f'Duplicate hits found these should have been merged. Output to {duplicate_hits_output}')

    out_dfs.to_csv(output_csv)

    return out_dfs
