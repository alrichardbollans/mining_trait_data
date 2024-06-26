import os

import numpy as np
import pandas as pd
from tqdm import tqdm

# Add progress bar to apply method
tqdm.pandas()

from pkg_resources import resource_filename

_inputs_path = resource_filename(__name__, 'inputs')
# Shapefile from https://github.com/tdwg/wgsrpd
tdwg3_shpfile = os.path.join(_inputs_path, 'wgsrpd-master', 'level3', 'level3.shp')


def get_tdwg_regions_for_occurrences(occ_df: pd.DataFrame) -> pd.DataFrame:
    """
    GET TDWG regions for occurrences
    :param occ_df:
    :return:
    """
    import geopandas

    print('Creating geometries from longitude and latitude')
    # changing to a GeoDataFrame to create geometry series
    occ_gp = geopandas.GeoDataFrame(occ_df,
                                    geometry=geopandas.points_from_xy(occ_df['decimalLongitude'],
                                                                      occ_df['decimalLatitude']))

    ## Add shapefile
    # set the filepath and load in a shapefile
    map_df = geopandas.read_file(tdwg3_shpfile)

    occ_gp['tdwg3_region'] = ''
    for idx in tqdm(range(map_df.shape[0]), desc="Getting tdwg regions for each occurrence…", ascii=False,
                    ncols=82):
        # For every location, find if they reside within a region
        pip = occ_gp.within(map_df.loc[idx, 'geometry'])
        if pip.sum() > 0:  # we found where some of the addresses reside at map_df.loc[idx]
            occ_gp.loc[pip, 'tdwg3_region'] = map_df.loc[idx, 'LEVEL3_COD']

    print(occ_gp)
    return occ_gp


def _find_whether_occurrences_in_native_or_introduced_regions(
        occ_df_with_acc_info_and_tdwg_regions: pd.DataFrame,
        output_csv: str = None,
        tdwg3_region_col_name: str = 'tdwg3_region', include_doubtful: bool = False,
        include_extinct: bool = False):
    """
    Use occurrence data with tdwg regions to find whether each occurrence is from a native or introduced region.
    Adds 'within_native' and 'within_introduced' columns to dataframe which are binary variables.
    :param occ_df_with_acc_info_and_tdwg_regions:
    :param distributions_csv:
    :param output_csv:
    :param tdwg3_region_col_name:
    :return:
    """
    from wcvpy.wcvp_download import get_distributions_for_accepted_taxa, native_code_column, \
        introduced_code_column, wcvp_accepted_columns
    print('Getting native/introduced data for taxa')
    ### Match taxa to WCVP regions
    merged = get_distributions_for_accepted_taxa(occ_df_with_acc_info_and_tdwg_regions,
                                                 wcvp_accepted_columns['name'],
                                                 include_doubtful, include_extinct)
    merged['within_native'] = merged.progress_apply(
        lambda x: np.nan if x[native_code_column] is np.nan else (
            1 if x[tdwg3_region_col_name] in x[native_code_column] else 0), axis=1)

    merged['within_introduced'] = merged.progress_apply(
        lambda x: np.nan if x[introduced_code_column] is np.nan else (
            1 if x[tdwg3_region_col_name] in x[introduced_code_column] else 0), axis=1)

    if output_csv is not None:
        merged.to_csv(output_csv)
    return merged


def clean_occurrences_by_tdwg_regions(occ_df: pd.DataFrame, name_column: str = 'scientificName',
                                      clean_by: str = 'native',
                                      output_csv: str = None, remove_duplicate_records: bool = True,
                                      remove_duplicated_lat_long_at_rank: str = None,
                                      include_doubtful: bool = False,
                                      include_extinct: bool = False, **kwargs):
    """
    Use distribution data to remove occurrences outside of native/introduced based on given priority.
    Distritbution data must be supplied for your families, which can be generated by wcvp_distributions
    :param include_extinct: bool whether to include extinct regions in distributions
    :param include_doubtful: bool whether to include doubtful regions in distributions
    :param remove_duplicated_lat_long_at_rank: string specifying removal of duplicates for given rank
    :param remove_duplicate_records: bool specifying whether to remove duplicate gbif records
    :param occ_df: dataframe of gbif occurrences
    :param clean_by: whether to include introduced regions in cleaning one of 'native' or 'both'
    :param output_csv:
    :return:
    """
    from wcvpy.wcvp_download import wcvp_accepted_columns
    from wcvpy.wcvp_name_matching import get_accepted_info_from_names_in_column

    occ_with_acc_info = get_accepted_info_from_names_in_column(occ_df, name_column, **kwargs)
    occ_with_acc_info = occ_with_acc_info.dropna(subset=wcvp_accepted_columns['name'])
    if remove_duplicate_records:
        print('Removing duplicate Gbif IDs')
        occ_with_acc_info = occ_with_acc_info.drop_duplicates(subset=['gbifID'], keep='first')

    if remove_duplicated_lat_long_at_rank is None:
        print('remove_duplicated_lat_long_at_rank not specified')

    else:
        if remove_duplicated_lat_long_at_rank.lower() == 'species':
            occ_with_acc_info = occ_with_acc_info.drop_duplicates(
                subset=[wcvp_accepted_columns['species'], 'decimalLatitude', 'decimalLongitude'],
                keep='first')
        elif remove_duplicated_lat_long_at_rank.lower() == 'precise':
            occ_with_acc_info = occ_with_acc_info.drop_duplicates(
                subset=[wcvp_accepted_columns['name'], 'decimalLatitude', 'decimalLongitude'], keep='first')

    occ_with_tdwg = get_tdwg_regions_for_occurrences(occ_with_acc_info)
    matched_tdwg_info = _find_whether_occurrences_in_native_or_introduced_regions(occ_with_tdwg,
                                                                                  include_doubtful=include_doubtful,
                                                                                  include_extinct=include_extinct)

    if clean_by == 'both':
        print('Allowing both native and introduced')
        out_occ_df = matched_tdwg_info[
            (matched_tdwg_info['within_native'] == 1) | (matched_tdwg_info['within_introduced'] == 1) | (
                    (matched_tdwg_info['within_native'].isna()) & (
                matched_tdwg_info['within_introduced'].isna()))]
    elif clean_by == 'native':
        print('Allowing only native occurrences')
        out_occ_df = matched_tdwg_info[
            (matched_tdwg_info['within_native'] == 1) | (matched_tdwg_info['within_native'].isna())]

    else:
        raise ValueError("clean_by must be one of 'native', 'both'")

    if output_csv is not None:
        out_occ_df.to_csv(output_csv)

    return out_occ_df
