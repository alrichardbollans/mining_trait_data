import os
import pandas as pd
from pkg_resources import resource_filename

from name_matching_cleaning import compile_hits, get_accepted_info_from_names_in_column
from powo_searches import search_powo

### Inputs
inputs_path = resource_filename(__name__, 'inputs')
initial_MPNS_csv = os.path.join(inputs_path, 'MPNS V11 subset Apocynaceae + Rubiaceae.csv')

### Temp outputs
temp_outputs_path = resource_filename(__name__, 'temp_outputs')
powo_search_medicinal_temp_output_accepted_csv = os.path.join(temp_outputs_path, 'powo_medicinal_accepted.csv')

cleaned_MPNS_accepted_csv = os.path.join(temp_outputs_path, 'MPNS Data_accepted.csv')

powo_search_malarial_temp_output_accepted_csv = os.path.join(temp_outputs_path, 'powo_malarial_accepted.csv')

### Outputs
output_path = resource_filename(__name__, 'outputs')
output_medicinal_csv = os.path.join(output_path, 'list_plants_medicinal_usage.csv')
output_malarial_csv = os.path.join(output_path, 'list_plants_malarial_usage.csv')


def get_powo_medicinal_usage():
    search_powo(
        ['medicinal', 'medication', 'medicine', 'therapeutic', 'healing', 'cure', 'drug', 'antibiotic', 'antiviral',
         'antibacterial'],
        powo_search_medicinal_temp_output_accepted_csv,
        characteristics_to_search=['use'],
        families_of_interest=['Rubiaceae', 'Apocynaceae'],
        filters=['species', 'infraspecies']
    )


def prepare_MPNS_common_names(families_of_interest=None) -> pd.DataFrame:
    # Requested from MPNS
    mpns_df = pd.read_csv(initial_MPNS_csv)
    mpns_df.drop(columns=['refstand', 'ref_short'], inplace=True)

    mpns_df = mpns_df.dropna(subset=['taxon_name'])
    if families_of_interest is not None:
        mpns_df = mpns_df[mpns_df['family'].str.contains('|'.join(families_of_interest))]

    mpns_df = mpns_df.drop_duplicates()
    accepted_mpns_df = get_accepted_info_from_names_in_column(mpns_df, 'taxon_name')

    accepted_mpns_df = accepted_mpns_df.dropna(subset=['Accepted_Name'])
    accepted_mpns_df['Source'] = 'MPNS ('+accepted_mpns_df['taxon_name'].astype(str)+')'

    accepted_mpns_df.to_csv(cleaned_MPNS_accepted_csv)

    return accepted_mpns_df


def get_powo_antimalarial_usage():
    search_powo(['antimalarial', 'malaria', 'antimalaria'],
                powo_search_malarial_temp_output_accepted_csv,
                characteristics_to_search=['use'],
                families_of_interest=['Rubiaceae', 'Apocynaceae'],
                filters=['species', 'infraspecies']
                )


def main():
    get_powo_medicinal_usage()
    prepare_MPNS_common_names(families_of_interest=['Apocynaceae', 'Rubiaceae'])
    powo_medicinal_hits = pd.read_csv(powo_search_medicinal_temp_output_accepted_csv)
    mpns_medicinal_hits = pd.read_csv(cleaned_MPNS_accepted_csv)
    compile_hits([powo_medicinal_hits, mpns_medicinal_hits], output_medicinal_csv)

    get_powo_antimalarial_usage()
    powo_antimalarial_hits = pd.read_csv(powo_search_malarial_temp_output_accepted_csv)
    compile_hits([powo_antimalarial_hits], output_malarial_csv)


if __name__ == '__main__':
    main()
