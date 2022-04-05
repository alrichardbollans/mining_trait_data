import os

import pandas as pd
from pkg_resources import resource_filename

from typing import List
from taxa_lists import get_all_taxa

from climate_vars import spec_occurenc_input, summary_output_csv

### Inputs
_inputs_path = resource_filename(__name__, 'inputs')
_clean_occurence_input_csv = os.path.join(_inputs_path, 'cleaned_species_occurences.csv')

### Temp outputs
_temp_outputs_path = resource_filename(__name__, 'temp_outputs')

### Outputs
_output_path = resource_filename(__name__, 'outputs')

if not os.path.isdir(_inputs_path):
    os.mkdir(_inputs_path)
if not os.path.isdir(_temp_outputs_path):
    os.mkdir(_temp_outputs_path)
if not os.path.isdir(_output_path):
    os.mkdir(_output_path)




def summarise():
    acc_sp = get_all_taxa(families_of_interest=['Apocynaceae', 'Rubiaceae'], accepted=True, ranks=['Species'])
    clean_occ_df = pd.read_csv(spec_occurenc_input)
    unique_species = clean_occ_df['species'].unique()


    out_dict = {'Total Species': [len(acc_sp.index)], 'Found Species': [len(unique_species)],
                'Percent': [float(len(unique_species)) / len(acc_sp.index)]}
    out_df = pd.DataFrame(out_dict)
    out_df.to_csv(summary_output_csv)


def main():
    summarise()


if __name__ == '__main__':
    main()
