import os

import pandas as pd
from automatchnames import get_accepted_info_from_names_in_column


def get_tempout_csv(dataset_name: str, temp_output_path: str):
    return os.path.join(temp_output_path, dataset_name + '_accepted.csv')


def generic_prepare_data(dataset_name: str, temp_output_path: str, df: pd.DataFrame, name_col: str,
                         source: str = None):
    if source is not None:
        df['Source'] = source
    db_acc = get_accepted_info_from_names_in_column(df, name_col)
    db_acc.to_csv(get_tempout_csv(dataset_name, temp_output_path))
