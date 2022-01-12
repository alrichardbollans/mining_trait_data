import os

import pandas as pd
from pkg_resources import resource_filename

from name_matching_cleaning import compile_hits
from powo_searches import search_powo, clean_powo_output

### Inputs


inputs_path = resource_filename(__name__, 'inputs')

### Temp outputs
temp_outputs_path = resource_filename(__name__, 'temp_outputs')
powo_search_medicinal_temp_output_csv = os.path.join(temp_outputs_path, 'powo_medicinal.csv')
powo_search_medicinal_temp_output_cleaned_csv = os.path.join(temp_outputs_path, 'powo_medicinal_cleaned.csv')

powo_search_malarial_temp_output_csv = os.path.join(temp_outputs_path, 'powo_malarial.csv')
powo_search_malarial_temp_output_cleaned_csv = os.path.join(temp_outputs_path, 'powo_malarial_cleaned.csv')

### Outputs
output_path = resource_filename(__name__, 'outputs')
output_medicinal_csv = os.path.join(output_path, 'list_plants_medicinal_usage.csv')
output_malarial_csv = os.path.join(output_path, 'list_plants_malarial_usage.csv')


def get_powo_medicinal_usage():
    search_powo('medicinal,medication,medicine,therapeutic,healing,cure,drug,antibiotic,antiviral,antibacterial',
                powo_search_medicinal_temp_output_csv, powo_search_medicinal_temp_output_cleaned_csv)


def get_powo_antimalarial_usage():
    search_powo('antimalarial,malaria,antimalaria',
                powo_search_malarial_temp_output_csv, powo_search_malarial_temp_output_cleaned_csv)


def main():
    get_powo_medicinal_usage()
    powo_medicinal_hits = pd.read_csv(powo_search_medicinal_temp_output_cleaned_csv)
    compile_hits([powo_medicinal_hits], output_medicinal_csv)

    get_powo_antimalarial_usage()
    powo_antimalarial_hits = pd.read_csv(powo_search_malarial_temp_output_cleaned_csv)
    compile_hits([powo_antimalarial_hits], output_malarial_csv)


if __name__ == '__main__':
    main()
