import os

import pandas as pd
import requests
from pkg_resources import resource_filename

# Add progress bar to apply method
from tqdm import tqdm

tqdm.pandas()

from plant_occurence_searches import cleaned_apoc_rub_occurences_csv

_output_path = resource_filename(__name__, 'outputs')
apocs_rubs_nitrogen_means = os.path.join(_output_path, 'apocs_rubs_nitrogen_soil_means.csv')
apocs_rubs_ph_means = os.path.join(_output_path, 'apocs_rubs_ph_soil_means.csv')


def get_mean_property_for_lat_long(lon: float, lat: float, prop: str):
    # TODO: add rate limiting protection
    response = requests.get(
        f'https://rest.isric.org/soilgrids/v2.0/properties/query?lon={lon}&lat={lat}&property={prop}&depth=0-5cm&value=mean').json()

    return response["properties"]["layers"][0]["depths"][0]["values"]["mean"]


def get_mean_property_for_row(row: pd.Series, prop: str):
    return get_mean_property_for_lat_long(row.decimalLongitude, row.decimalLatitude, prop)


def add_property_means(df_of_occurences: pd.DataFrame, prop: str):
    # Only search for unique cases
    unique_longs_and_lats = df_of_occurences.drop_duplicates(subset=['decimalLongitude', 'decimalLatitude'])
    unique_longs_and_lats[prop] = unique_longs_and_lats.progress_apply(get_mean_property_for_row, axis=1,
                                                                       prop=prop)
    unique_longs_and_lats = unique_longs_and_lats[['decimalLongitude', 'decimalLatitude', prop]]
    # Merge into original
    out_df = df_of_occurences.merge(unique_longs_and_lats, on=['decimalLongitude', 'decimalLatitude'],
                                    how='left').set_index(df_of_occurences.index)

    return out_df


def _get_nitrogen_means():
    occ_df = pd.read_csv(cleaned_apoc_rub_occurences_csv, index_col=0)
    with_nitrogen = add_property_means(occ_df, 'nitrogen')
    with_nitrogen.to_csv(apocs_rubs_nitrogen_means)


def _get_ph_means():
    occ_df = pd.read_csv(cleaned_apoc_rub_occurences_csv, index_col=0)
    with_ph = add_property_means(occ_df, 'phh2o')
    with_ph.to_csv(apocs_rubs_ph_means)


if __name__ == "__main__":
    _get_nitrogen_means()
    _get_ph_means()
