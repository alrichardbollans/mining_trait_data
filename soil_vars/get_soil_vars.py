import pandas as pd
import requests
from pkg_resources import resource_filename

# Add progress bar to apply method
from tqdm import tqdm
tqdm.pandas()

_output_path = resource_filename(__name__, 'outputs')


def get_mean_property_for_lat_long(lat: float, lon: float, prop: str):
    # TODO: add rate limiting protection
    response = requests.get(
        f'https://rest.isric.org/soilgrids/v2.0/properties/query?lon={lon}&lat={lat}&property={prop}&depth=0-5cm&value=mean').json()

    return response["properties"]["layers"][0]["depths"][0]["values"]["mean"]


def get_mean_property_for_row(row: pd.Series, prop: str):
    return get_mean_property_for_lat_long(row.decimalLatitude, row.decimalLongitude, prop)


def add_nitrogen_means(df_of_occurences: pd.DataFrame):
    df_of_occurences['nitrogen'] = df_of_occurences.progress_apply(get_mean_property_for_row, axis=1, prop='nitrogen')

    return df_of_occurences

# if __name__ == "__main__":
#     add_nitrogen_means()
