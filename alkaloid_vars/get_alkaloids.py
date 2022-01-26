import os

import pandas as pd
from pkg_resources import resource_filename

from name_matching_cleaning import compile_hits
from powo_searches import search_powo

### Inputs
inputs_path = resource_filename(__name__, 'inputs')

### Temp outputs
temp_outputs_path = resource_filename(__name__, 'temp_outputs')
powo_search_temp_output_csv = os.path.join(temp_outputs_path, 'powo_alkaloids.csv')
powo_search_temp_output_cleaned_csv = os.path.join(temp_outputs_path, 'powo_alkaloids_cleaned.csv')

### Outputs
output_path = resource_filename(__name__, 'outputs')
output_alkaloid_csv = os.path.join(output_path, 'list_plants_with_alkaloids.csv')


def get_powo_alkaloids():
    search_powo(['alkaloids', 'alkaloid', 'bitter', 'amine'], powo_search_temp_output_csv,
                powo_search_temp_output_cleaned_csv, families_of_interest=['Rubiaceae', 'Apocynaceae'],
                filters=['species', 'infraspecies'])


def main():
    get_powo_alkaloids()
    powo_hits = pd.read_csv(powo_search_temp_output_cleaned_csv)
    compile_hits([powo_hits], output_alkaloid_csv)


if __name__ == '__main__':
    main()
