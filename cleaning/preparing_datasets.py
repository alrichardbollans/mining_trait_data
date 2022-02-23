import os

import pandas as pd
from automatchnames import get_accepted_info_from_names_in_column
from typing import List


def get_tempout_csv(dataset_name: str, temp_output_path: str):
    return os.path.join(temp_output_path, dataset_name + '_accepted.csv')


def generic_prepare_data(dataset_name: str, temp_output_path: str, df: pd.DataFrame, name_col: str,
                         dropifna: List[str] = None, families_of_interest: List[str]=None):
    if dropifna is not None:
        df.dropna(subset=dropifna, inplace=True)
    df['Source'] = dataset_name
    db_acc = get_accepted_info_from_names_in_column(df, name_col,families_of_interest=families_of_interest)
    db_acc.to_csv(get_tempout_csv(dataset_name, temp_output_path))
