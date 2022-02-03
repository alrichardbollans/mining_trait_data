import os

import pandas as pd
from pkg_resources import resource_filename

from name_matching_cleaning import compile_hits
from powo_searches import search_powo

### Inputs
_inputs_path = resource_filename(__name__, 'inputs')

### Temp outputs
_temp_outputs_path = resource_filename(__name__, 'temp_outputs')
_powo_search_temp_output_accepted_csv = os.path.join(_temp_outputs_path, 'powo_alkaloids_accepted.csv')

### Outputs
_output_path = resource_filename(__name__, 'outputs')
output_alkaloid_csv = os.path.join(_output_path, 'list_plants_with_alkaloids.csv')


def get_powo_alkaloids():
    search_powo(['alkaloids', 'alkaloid', 'bitter', 'amine'],
                _powo_search_temp_output_accepted_csv, families_of_interest=['Rubiaceae', 'Apocynaceae'],
                filters=['species', 'infraspecies'])


def main():
    get_powo_alkaloids()
    powo_hits = pd.read_csv(_powo_search_temp_output_accepted_csv)
    compile_hits([powo_hits], output_alkaloid_csv)


if __name__ == '__main__':
    main()
