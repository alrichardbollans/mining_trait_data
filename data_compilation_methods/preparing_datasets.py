import os

import numpy as np
import pandas as pd
from wcvp_name_matching import get_accepted_info_from_names_in_column
from typing import List

from tqdm import tqdm


def get_tempout_csv(dataset_name: str, temp_output_path: str):
    return os.path.join(temp_output_path, dataset_name + '_accepted.csv')


def generic_prepare_data(dataset_name: str, temp_output_path: str, df: pd.DataFrame, name_col: str,
                         snippet_column: str,
                         dropifna: List[str] = None, families_of_interest: List[str] = None,
                         batch: bool = False, family_column: str = None):
    if dropifna is not None:
        df.dropna(subset=dropifna, inplace=True)
    df['Source'] = dataset_name
    df[dataset_name + '_Snippet'] = df[snippet_column]
    if batch:
        n = int(len(df.index) / 1000) + 1
        list_df = np.array_split(df, n)
        acc_dfs = []

        for i in tqdm(range(len(list_df)), desc="Finding names", ascii=False, ncols=72):
            split_df = list_df[i]
            acc_dfs.append(
                get_accepted_info_from_names_in_column(split_df, name_col,
                                                       families_of_interest=families_of_interest,
                                                       family_column=family_column))
        db_acc = pd.concat(acc_dfs)
    else:
        db_acc = get_accepted_info_from_names_in_column(df, name_col,
                                                        families_of_interest=families_of_interest,
                                                        family_column=family_column)
    db_acc.to_csv(get_tempout_csv(dataset_name, temp_output_path))
