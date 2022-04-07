import os

import numpy as np
import pandas as pd

from tqdm import tqdm

from climate_vars import spec_occurence_input, climate_temp_outputs_path

tqdm.pandas()

import requests
from pkg_resources import resource_filename
from pygbif import occurrences as occ

spec_elevations_csv = os.path.join(climate_temp_outputs_path, 'cleaned_species_occurences_w_elevation.csv')
elevation_batch_dir = os.path.join(climate_temp_outputs_path, 'elevation_batches')


def get_elevation_from_gbif_key(gbifkey: int):
    gbifkey = int(gbifkey)

    # Note package issue https://github.com/gbif/pygbif/issues/93
    try:
        record = occ.get(key=gbifkey)

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:

            return np.nan
        else:
            print(e)
            print(gbifkey)
            return 'retry'

    try:
        return record['elevation']
    except KeyError:
        return np.nan


def append_elevation_to_occurences(occ_df: pd.DataFrame) -> pd.DataFrame:
    occ_df['elevation'] = occ_df['gbifID'].progress_apply(get_elevation_from_gbif_key)

    return occ_df


def batch_append_elevation(occ_df: pd.DataFrame, start_from=0):
    n = int(len(occ_df.index) / 1000) + 1
    list_df = np.array_split(occ_df, n)

    for i in tqdm(range(len(list_df)), desc="Iterating over dfs", ascii=False, ncols=72):
        if i >= start_from:
            split_df = list_df[i]
            split_df['elevation'] = split_df['gbifID'].progress_apply(get_elevation_from_gbif_key)
            split_df.to_csv(os.path.join(elevation_batch_dir, str(i) + '.csv'))


def recompile_batches() -> pd.DataFrame:
    collect_dfs = []
    batch_files = os.listdir(elevation_batch_dir)
    csv_files = [f for f in batch_files if f.endswith('.csv')]
    for csv_file in csv_files:
        collect_dfs.append(pd.read_csv(csv_file,
                                       usecols=['species', 'fullname', 'decimalLongitude', 'decimalLatitude', 'gbifID',
                                                'elevation']))
    recompiled_df = pd.concat(collect_dfs)

    return recompiled_df


def check_outputs():
    recompiled_df = recompile_batches()
    cases_to_retry = recompiled_df[recompiled_df['elevation'] == 'retry']
    if len(cases_to_retry.index) > 0:
        print('Some cases to retry')
        print(cases_to_retry)
        cases_to_retry.to_csv(os.path.join(climate_temp_outputs_path, 'elevation_cases_to_retry.csv'))

    else:
        print('No cases to retry')
    recompiled_without_el = recompiled_df.drop(columns=['elevation'])
    clean_occ_df = pd.read_csv(spec_occurence_input,
                               usecols=['species', 'fullname', 'decimalLongitude', 'decimalLatitude', 'gbifID'])
    pd.testing.assert_frame_equal(recompiled_without_el, clean_occ_df)


def main():
    ## Add elevation
    clean_occ_df = pd.read_csv(spec_occurence_input,
                               usecols=['species', 'fullname', 'decimalLongitude', 'decimalLatitude', 'gbifID'])
    batch_append_elevation(clean_occ_df,start_from=44)


if __name__ == '__main__':
    main()
