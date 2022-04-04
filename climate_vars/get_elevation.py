import os

import numpy as np
import pandas as pd

from tqdm import tqdm
tqdm.pandas()

import requests
from pkg_resources import resource_filename
from pygbif import occurrences as occ

_inputs_path = resource_filename(__name__, 'inputs')
_spec_occurenc_input = os.path.join(_inputs_path, 'cleaned_species_occurences.csv')

_temp_outputs_path = resource_filename(__name__, 'temp_outputs')
_spec_elevations_csv = os.path.join(_temp_outputs_path, 'cleaned_species_occurences_w_elevation.csv')

_output_path = resource_filename(__name__, 'outputs')
if not os.path.isdir(_inputs_path):
    os.mkdir(_inputs_path)
if not os.path.isdir(_temp_outputs_path):
    os.mkdir(_temp_outputs_path)
if not os.path.isdir(_output_path):
    os.mkdir(_output_path)


def get_elevation_from_gbif_key(gbifkey: int):
    gbifkey = int(gbifkey)
    print(gbifkey)
    # Note package issue https://github.com/gbif/pygbif/issues/93
    try:
        record = occ.get(key=gbifkey)

    except requests.exceptions.HTTPError as e:

        print(e)
        return np.nan

    try:
        return record['elevation']
    except KeyError:
        return np.nan


def append_elevation_to_occurences(occ_df: pd.DataFrame) -> pd.DataFrame:
    occ_df['elevation'] = occ_df['gbifID'].progress_apply(get_elevation_from_gbif_key)

    return occ_df


def plot_sp_map():
    # Note package issue: https://github.com/gbif/pygbif/issues/86
    from pygbif import maps
    out = maps.map(taxonKey=1)
    print(out.response)
    print(out.path)
    print(out.img)
    out.plot()


def main():
    ## Add elevation
    clean_occ_df = pd.read_csv(_spec_occurenc_input)
    w_elevation = append_elevation_to_occurences(clean_occ_df)
    w_elevation.to_csv(_spec_elevations_csv)


if __name__ == '__main__':
    main()
