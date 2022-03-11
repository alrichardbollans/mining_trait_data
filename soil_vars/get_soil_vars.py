import pandas as pd
import requests
from pkg_resources import resource_filename

# Add progress bar to apply method
from tqdm import tqdm

tqdm.pandas()

_output_path = resource_filename(__name__, 'outputs')


def get_mean_property_for_lat_long(lon: float, lat: float, prop: str):
    # TODO: add rate limiting protection
    response = requests.get(
        f'https://rest.isric.org/soilgrids/v2.0/properties/query?lon={lon}&lat={lat}&property={prop}&depth=0-5cm&value=mean').json()

    return response["properties"]["layers"][0]["depths"][0]["values"]["mean"]


def get_mean_property_for_row(row: pd.Series, prop: str):
    return get_mean_property_for_lat_long(row.decimalLongitude, row.decimalLatitude, prop)


def add_nitrogen_means(df_of_occurences: pd.DataFrame):
    # Only search for unique cases
    unique_longs_and_lats = df_of_occurences.drop_duplicates(subset=['decimalLongitude', 'decimalLatitude'])
    unique_longs_and_lats['nitrogen'] = unique_longs_and_lats.progress_apply(get_mean_property_for_row, axis=1,
                                                                             prop='nitrogen')
    unique_longs_and_lats = unique_longs_and_lats[['decimalLongitude', 'decimalLatitude', 'nitrogen']]
    # Merge into original
    out_df = df_of_occurences.merge(unique_longs_and_lats, on=['decimalLongitude', 'decimalLatitude'],
                                                  how='left').set_index(df_of_occurences.index)

    return out_df

# if __name__ == "__main__":
#     add_nitrogen_means()
