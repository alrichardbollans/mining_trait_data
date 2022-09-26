import os
from typing import List

import pandas as pd
# Add progress bar to apply method

from tqdm import tqdm

tqdm.pandas()

from pkg_resources import resource_filename

_inputs_path = resource_filename(__name__, 'inputs')
# Shapefile from https://github.com/tdwg/wgsrpd
tdwg3_shpfile = os.path.join(_inputs_path, 'wgsrpd-master', 'level3', 'level3.shp')


def read_occurences_and_output_acc_names(occ_df: pd.DataFrame, out_csv: str = None,
                                         families_in_occurrences: List[str] = None) -> pd.DataFrame:
    """
    Get accepted info for occurrences.
    :return:
    """
    from automatchnames import get_accepted_info_from_names_in_column

    print('Getting accepted info for occurrences:')
    print(occ_df)
    occ_df = occ_df.drop_duplicates(subset=['gbifID'], keep='first')

    acc_df = get_accepted_info_from_names_in_column(occ_df, 'fullname',
                                                    families_of_interest=families_in_occurrences)

    if out_csv is not None:
        acc_df.to_csv(out_csv)

    return acc_df


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
    for idx in tqdm(range(map_df.shape[0]), desc="Getting tdwg regions for each occurrence…", ascii=False, ncols=72):
        # For every location, find if they reside within a region
        pip = occ_gp.within(map_df.loc[idx, 'geometry'])
        if pip.sum() > 0:  # we found where some of the addresses reside at map_df.loc[idx]
            occ_gp.loc[pip, 'tdwg3_region'] = map_df.loc[idx, 'LEVEL3_COD']

    print(occ_gp)
    return occ_gp


def find_whether_occurrences_in_native_or_introduced_regions(
        occ_df_with_acc_info_and_tdwg_regions: pd.DataFrame,
        distributions_csv: str,
        output_csv: str = None,
        tdwg3_region_col_name: str = 'tdwg3_region'):
    """
    Use occurrence data with tdwg regions to find whether each occurrence is from a native or introduced region.
    Adds 'within_native' and 'within_introduced' columns to dataframe which are binary variables.
    :param occ_df_with_acc_info_and_tdwg_regions:
    :param distributions_csv:
    :param output_csv:
    :param tdwg3_region_col_name:
    :return:
    """
    import ast
    print('Getting native/introduced data for taxa')
    ### Match taxa to wcsp regions
    distro_df = pd.read_csv(distributions_csv)[
        ['native_tdwg3_codes', 'intro_tdwg3_codes', 'extinct_tdwg3_codes', 'Accepted_ID']]
    merged = pd.merge(occ_df_with_acc_info_and_tdwg_regions, distro_df, on='Accepted_ID')

    merged['within_native'] = merged.progress_apply(
        lambda x: 1 if x[tdwg3_region_col_name] in ast.literal_eval(x['native_tdwg3_codes']) else 0, axis=1)

    merged['within_introduced'] = merged.progress_apply(
        lambda x: 1 if x[tdwg3_region_col_name] in ast.literal_eval(x['intro_tdwg3_codes']) else 0, axis=1)

    if output_csv is not None:
        merged.to_csv(output_csv)
    return merged

def clean_occurrences_by_tdwg_regions(occ_with_acc_info: pd.DataFrame,
                                      distributions_csv: str,
                                      priority: str = 'native',
                                      output_csv: str = None, remove_duplicate_records: bool = True,
                                      remove_duplicated_lat_long_at_rank: str = 'precise'):
    """
    Use distribution data to remove occurrences outside of native/introduced based on given priority.
    Distritbution data must be supplied for your families, which can be generated by wcsp_distribution_search
    :param occ_with_acc_info:
    :param distributions_csv:
    :param priority:
    :param output_csv:
    :return:
    """

    if remove_duplicate_records:
        print('Removing duplicate Gbif IDs')
        occ_with_acc_info = occ_with_acc_info.drop_duplicates(subset=['gbifID'], keep='first')

    if remove_duplicated_lat_long_at_rank == 'species':
        occ_with_acc_info = occ_with_acc_info.drop_duplicates(
            subset=['Accepted_Species', 'decimalLatitude', 'decimalLongitude'], keep='first')
    elif remove_duplicated_lat_long_at_rank == 'precise':
        occ_with_acc_info = occ_with_acc_info.drop_duplicates(
            subset=['Accepted_Name', 'decimalLatitude', 'decimalLongitude'], keep='first')
    else:
        print('remove_duplicated_lat_long_at_rank not specified')

    occ_with_tdwg = get_tdwg_regions_for_occurrences(occ_with_acc_info)
    matched_tdwg_info = find_whether_occurrences_in_native_or_introduced_regions(occ_with_tdwg, distributions_csv)

    occ_in_native = matched_tdwg_info[(matched_tdwg_info['within_native'] == 1)]
    occ_in_introduced = matched_tdwg_info[(matched_tdwg_info['within_introduced'] == 1)]

    if priority == 'native_then_introduced':
        print('Prioritising native, then introduced')

        introd_occ_not_in_native = occ_in_introduced[
            ~occ_in_introduced['Accepted_ID'].isin(occ_in_native['Accepted_ID'].values)]
        out_occ_df = pd.concat([occ_in_native, introd_occ_not_in_native])

    elif priority == 'both':
        print('Allowing both native and introduced')
        out_occ_df = matched_tdwg_info[
            (matched_tdwg_info['within_native'] == 1) | (matched_tdwg_info['within_introduced'] == 1)]
    elif priority == 'native':
        print('Allowing only native occurrences')
        out_occ_df = occ_in_native

    else:
        raise ValueError("priority must be one of 'native', 'both' or 'native_then_introduced'")

    if output_csv is not None:
        out_occ_df.to_csv(output_csv)

    return out_occ_df
