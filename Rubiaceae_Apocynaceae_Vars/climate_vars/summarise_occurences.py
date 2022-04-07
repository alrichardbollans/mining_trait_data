import os

import pandas as pd
from pkg_resources import resource_filename

from typing import List
from taxa_lists import get_all_taxa

from climate_vars import spec_occurence_input, summary_output_csv


def summarise():
    acc_sp = get_all_taxa(families_of_interest=['Apocynaceae', 'Rubiaceae'], accepted=True, ranks=['Species'])
    clean_occ_df = pd.read_csv(spec_occurence_input)
    unique_species = clean_occ_df['species'].unique()


    out_dict = {'Total Species': [len(acc_sp.index)], 'Found Species': [len(unique_species)],
                'Percent': [float(len(unique_species)) / len(acc_sp.index)]}
    out_df = pd.DataFrame(out_dict)
    out_df.to_csv(summary_output_csv)

def plot_sp_map():
    # Note package issue: https://github.com/gbif/pygbif/issues/86
    from pygbif import maps
    out = maps.map(taxonKey=1)
    print(out.response)
    print(out.path)
    print(out.img)
    out.plot()

def main():
    summarise()


if __name__ == '__main__':
    main()
