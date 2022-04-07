import os

import pandas as pd
from automatchnames import get_accepted_info_from_names_in_column
from pkg_resources import resource_filename
from taxa_lists import get_all_taxa
from typing import List

_inputs_path = resource_filename(__name__, 'inputs')

_temp_outputs_path = resource_filename(__name__, 'temp_outputs')


_output_path = resource_filename(__name__, 'outputs')
compiled_climate_vars_csv = os.path.join(_output_path,'compiled_climate_vars.csv')

if not os.path.isdir(_temp_outputs_path):
    os.mkdir(_temp_outputs_path)
if not os.path.isdir(_output_path):
    os.mkdir(_output_path)




def get_median_df():
    # TODO: add elevation
    # We take median of occurences in order to mitigate outliers
    # This still has the possible issue of being biased towards where people take samples

    clim_occ_df =pd.read_csv(os.path.join(_temp_outputs_path,'species_with_clim_vars.csv'))
    print(clim_occ_df.head())
    print(clim_occ_df.columns)
    dfs = []
    for c in ['CHELSA_bio1_1981.2010_V.2.1', 'CHELSA_bio12_1981.2010_V.2.1',
       'nitrogen_0.5cm_mean', 'phh2o_0.5cm_mean']:
        avg = pd.DataFrame(clim_occ_df.groupby([clim_occ_df['fullname']])[c].median())

        dfs.append(avg)

    for df in dfs:
        print(len(df))
    merged = pd.merge(dfs[0],dfs[1], on='fullname')
    merged = pd.merge(merged,dfs[2],on='fullname')
    merged = pd.merge(merged, dfs[3],on='fullname')
    merged['fullname'] = merged.index
    acc_merged = get_accepted_info_from_names_in_column(merged,'fullname',families_of_interest=['Apocynaceae','Rubiaceae'])
    acc_merged.to_csv(compiled_climate_vars_csv)


def main():
    get_median_df()


if __name__ == '__main__':
    main()
