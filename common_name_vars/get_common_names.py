import os.path
import urllib.request
from urllib.error import HTTPError

import numpy as np
import pandas as pd
from typing import List

import wikipedia_searches
from pkg_resources import resource_filename

from name_matching_cleaning import standardise_names_in_column, clean_ids, get_accepted_name_info_from_IDS, compile_hits

### Inputs
inputs_path = resource_filename(__name__, 'inputs')
input_species_csv = os.path.join(inputs_path, 'clean.csv')
initial_USDA_csv = os.path.join(inputs_path, 'USDA Plants Database.csv')
ppa_africa_csv = os.path.join(inputs_path, 'PPAfrica-botswana-commonnames', 'vernacularname.txt')
species_profile_csv = os.path.join(inputs_path, 'SpeciesProfileVernacular', 'vernacular.tab')

### Temp outputs
temp_outputs_path = resource_filename(__name__, 'temp_outputs')

wiki_common_names_temp_output_csv = os.path.join(temp_outputs_path, 'wiki_common_name_hits.csv')
powo_common_names_temp_output_csv = os.path.join(temp_outputs_path, 'powo_common_name_hits.csv')
cleaned_USDA_csv = os.path.join(temp_outputs_path, 'USDA Plants Database_cleaned.csv')
spp_ppa_common_names_temp_output_csv = os.path.join(temp_outputs_path, 'spp_ppa_common_names.csv')

# Standardised versions
spp_ppa_common_names_temp_output_accepted_csv = os.path.join(temp_outputs_path, 'spp_ppa_common_names_accepted.csv')
wiki_common_names_temp_output_accepted_csv = os.path.join(temp_outputs_path, 'wiki_common_name_hits_accepted.csv')
powo_common_names_temp_output_accepted_csv = os.path.join(temp_outputs_path, 'powo_common_name_hits_accepted.csv')
cleaned_USDA_accepted_csv = os.path.join(temp_outputs_path, 'USDA Plants Database_cleaned_accepted.csv')

### Outputs
output_path = resource_filename(__name__, 'outputs')
output_common_names_csv = os.path.join(output_path, 'list_of_plants_with_common_names.csv')


def prepare_usda_common_names(families_of_interest=None):
    if families_of_interest is None:
        families_of_interest = ['Apocynaceae', 'Rubiaceae']

    # Copied from https://plants.usda.gov/csvdownload?plantLst=plantCompleteList
    usda_df = pd.read_csv(initial_USDA_csv)
    usda_df.drop(columns=['Symbol', 'Synonym Symbol'], inplace=True)
    usda_df = usda_df.rename(columns={'Common Name': 'USDA_Snippet'})
    usda_df = usda_df.dropna(subset=['USDA_Snippet'])
    usda_df = usda_df[usda_df['Family'].str.contains('|'.join(families_of_interest))]
    usda_df.to_csv(cleaned_USDA_csv)

    standardise_names_in_column('Scientific.Name.with.Author', cleaned_USDA_csv, cleaned_USDA_accepted_csv)

    accepted_usda_df = pd.read_csv(cleaned_USDA_accepted_csv)
    accepted_usda_df = accepted_usda_df.dropna(subset=['Accepted_Name'])
    accepted_usda_df = accepted_usda_df[accepted_usda_df['Accepted_Rank'] == 'Species']
    accepted_usda_df['Source'] = 'USDA Plants Database'

    accepted_usda_df.drop(columns=['X'], inplace=True)

    accepted_usda_df.to_csv(cleaned_USDA_accepted_csv)

    return accepted_usda_df


def prepare_common_names_spp_ppa() -> pd.DataFrame:
    # TODO: Note this data is not specific to any family
    species_profile = pd.read_csv(species_profile_csv, sep='\t', header=None)

    species_profile['Source'] = 'SpeciesProfileVernacular'
    species_profile['SPP_Snippet'] = species_profile[1] + ":" + species_profile[2]
    species_profile['ID'] = species_profile[0].apply(clean_ids)
    species_profile.drop(columns=[0, 1, 2, 3], inplace=True)

    ppa_africa = pd.read_csv(ppa_africa_csv, sep='\t', header=None)
    ppa_africa['Source'] = 'PPAfrica-botswana-commonnames'
    ppa_africa['PPA_Snippet'] = ppa_africa[3] + ":" + ppa_africa[2]
    ppa_africa['ID'] = ppa_africa[0].apply(clean_ids)
    ppa_africa.drop(columns=[0, 1, 2, 3, 4], inplace=True)

    merged = pd.merge(ppa_africa, species_profile, on="ID", how="outer")
    merged.to_csv(spp_ppa_common_names_temp_output_csv)
    get_accepted_name_info_from_IDS('ID', spp_ppa_common_names_temp_output_csv,
                                    spp_ppa_common_names_temp_output_accepted_csv)

    with_accepted_info = pd.read_csv(spp_ppa_common_names_temp_output_accepted_csv)

    return with_accepted_info


def get_powo_common_names(species_names: List[str], species_ids: List[str]) -> pd.DataFrame:
    '''
    Searches POWO for species names which have a common names section.
    :param species_names:
    :param species_ids:
    :return:
    '''
    out_dict = {'Name': [], 'POWO_Snippet': [], 'Source': []}
    for i in range(0, len(species_names)):
        try:
            name = species_names[i]
            id = species_ids[i]

            fp = urllib.request.urlopen("https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:" + str(id))
            mybytes = fp.read()

            mystr = mybytes.decode("utf8")
            fp.close()
            # print(mystr)
            common_name_section = '<section id="vernacular-names" class="c-article-section">'
            if common_name_section in mystr:
                i = mystr.index(common_name_section)
                snippet = mystr[i - 1:i + len(common_name_section) + 1]
                out_dict['Name'].append(name)
                out_dict['POWO_Snippet'].append(snippet)
                out_dict['Source'].append('POWO pages(' + str(id) +')')
        except HTTPError:
            print(f'Couldnt find id: {species_ids[i]}')
    df = pd.DataFrame(out_dict)

    df.to_csv(powo_common_names_temp_output_csv)
    return df


def get_wiki_common_names(species_names: List[str]):
    wikipedia_searches.search_for_common_names(species_names, wiki_common_names_temp_output_csv)


def standardise_names():
    standardise_names_in_column('Name', wiki_common_names_temp_output_csv, wiki_common_names_temp_output_accepted_csv)
    standardise_names_in_column('Name', powo_common_names_temp_output_csv, powo_common_names_temp_output_accepted_csv)

    # R imports col names with spaces as full stops
    prepare_usda_common_names()
    prepare_common_names_spp_ppa()


def main():
    # # # TODO: Note powo, wikipedia and USDA data is specific to our study
    species_data = pd.read_csv(input_species_csv)
    species_data.set_index('Accepted_Name', inplace=True)
    species_list = species_data.index

    # Get lists
    get_wiki_common_names(species_list)
    print('Finished getting wiki names')
    get_powo_common_names(species_list, species_data['Accepted_ID'].values)
    print('Finished getting powo names')

    standardise_names()
    print('Finished standardising names')

    usda_hits = pd.read_csv(cleaned_USDA_accepted_csv)
    spp_ppa_df = pd.read_csv(spp_ppa_common_names_temp_output_accepted_csv)
    powo_hits = pd.read_csv(powo_common_names_temp_output_accepted_csv)
    wiki_hits = pd.read_csv(wiki_common_names_temp_output_accepted_csv)

    all_dfs = [usda_hits, powo_hits, wiki_hits, spp_ppa_df]
    compile_hits(all_dfs, output_common_names_csv)


if __name__ == '__main__':
    main()
