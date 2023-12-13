from typing import List

import pandas as pd


def simplify_inchi_key(inch: str):
    # Using the connectivity layer of the InChIKey, i.e. the first 14 characters, to simplify.
    # As in e.g. https://www.sciencedirect.com/science/article/abs/pii/S2352007822002372 https://pubs.acs.org/doi/abs/10.1007/s13361-016-1589-4
    if inch == inch:
        return inch[:14]
    else:
        return inch

def filter_rows_containing_compound_keyword(df: pd.DataFrame, cols: List[str], keyword: str):
    # Initialize an empty DataFrame to store the filtered rows
    filtered_df = pd.DataFrame()
    negative_filtered_df = pd.DataFrame()
    nan_df = pd.DataFrame()
    # Iterate through the rows of the original DataFrame
    for index, row in df.iterrows():
        # Iterate through the specified columns
        if any(keyword in str(row[col]).lower() for col in cols):
            # If the keyword is found, add the entire row to the filtered DataFrame
            filtered_df = pd.concat([filtered_df, df.iloc[[index]]])

        elif all((str(row[col]) == '' or str(row[col]) == 'nan' or row[col] != row[col]) for col in cols):
            nan_df = pd.concat([nan_df, df.iloc[[index]]])
        else:
            negative_filtered_df = pd.concat([negative_filtered_df, df.iloc[[index]]])
    # Reset the index of the filtered DataFrame
    filtered_df.reset_index(drop=True, inplace=True)
    negative_filtered_df.reset_index(drop=True, inplace=True)
    nan_df.reset_index(drop=True, inplace=True)

    assert len(df.index) == (len(filtered_df.index) + len(negative_filtered_df.index)) + len(nan_df.index)

    return filtered_df, negative_filtered_df, nan_df