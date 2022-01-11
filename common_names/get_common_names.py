import os.path
import urllib.request
from urllib.error import HTTPError

import pandas as pd
from typing import List

import wikipedia_searches
from pkg_resources import resource_filename

from name_matching_cleaning import standardise_names_in_column, batch_standardise_names

inputs_path = resource_filename(__name__, 'inputs')
temp_outputs_path = resource_filename(__name__, 'temp_outputs')

wiki_common_names_temp_output_csv = os.path.join(temp_outputs_path, 'wiki_common_name_hits.csv')
powo_common_names_temp_output_csv = os.path.join(temp_outputs_path, 'powo_common_name_hits.csv')
initial_USDA_csv = os.path.join(inputs_path, 'USDA Plants Database.csv')
cleaned_USDA_csv = os.path.join(inputs_path, 'USDA Plants Database_cleaned.csv')
ppa_africa_csv = os.path.join(inputs_path, 'PPAfrica-botswana-commonnames', 'vernacularname.txt')
species_profile_csv = os.path.join(inputs_path, 'SpeciesProfileVernacular', 'vernacular.tab')


def clean_usda_names(families_of_interest=None):
    if families_of_interest is None:
        families_of_interest = ['Apocynaceae', 'Rubiaceae']

    def first_cleaning(given_name: str) -> str:
        out = given_name.replace(' ×', ' ')
        return out

    def second_cleaning(given_name: str) -> str:
        out = given_name.replace('×', '')
        return out

    # Copied from https://plants.usda.gov/csvdownload?plantLst=plantCompleteList
    usda_df = pd.read_csv(initial_USDA_csv)
    usda_df['Scientific Name with Author'] = usda_df['Scientific Name with Author'].apply(first_cleaning)
    usda_df['Scientific Name with Author'] = usda_df['Scientific Name with Author'].apply(second_cleaning)
    usda_df = usda_df.dropna(subset=['Common Name'])
    usda_df = usda_df[usda_df['Family'].str.contains('|'.join(families_of_interest))]


    usda_df.to_csv(cleaned_USDA_csv)


def get_UDSA_info() -> pd.DataFrame:
    # First add accepted names using KNMS (http://namematch.science.kew.org/csv)
    # Get expanded, data has a header, POWO
    # Need to clean the downloaded version first. Use 'USDA Plants Database_cleaned.csv' See clean_usda_names
    # usda_csv = os.path.join(inputs_path, 'USDA Plants Database_matched_1641569303504.csv')
    # usda_df = pd.read_csv(usda_csv, sep='\t')
    usda_df = pd.read_csv(cleaned_USDA_csv)
    # Drop rows with NaN common names
    # usda_df = usda_df.rename(columns={'Scientific Name': 'Name', 'Common Name': 'USDA_Snippet'})
    usda_df = usda_df.dropna(subset=['Common Name'])
    usda_df = usda_df.dropna(subset=['Accepted_Name'])
    usda_df = usda_df[usda_df['Rank'] == 'SPECIES']
    usda_df['Source'] = 'USDA Plants Database'

    usda_df.drop(columns=['Symbol', 'Synonym Symbol'], inplace=True)

    return usda_df


def get_common_names_spp_ppa() -> pd.DataFrame:
    species_profile = pd.read_csv(species_profile_csv, sep='\t', header=None)

    species_profile['Source'] = 'SpeciesProfileVernacular'
    species_profile['SPP_Snippet'] = species_profile[1] + ":" + species_profile[2]
    species_profile['ID'] = species_profile[0]
    species_profile.drop(columns=[0, 1, 2, 3], inplace=True)

    ppa_africa = pd.read_csv(ppa_africa_csv, sep='\t', header=None)

    ppa_africa['Source'] = 'PPAfrica-botswana-commonnames'
    ppa_africa['PPA_Snippet'] = ppa_africa[3] + ":" + ppa_africa[2]
    ppa_africa['ID'] = ppa_africa[0]
    ppa_africa.drop(columns=[0, 1, 2, 3, 4], inplace=True)

    species_profile.to_csv('temp_outputs/spprofile_common_names.csv')

    merged = pd.merge(ppa_africa, species_profile, on="ID", how="outer")

    return merged


def get_powo_common_names(species_names: List[str], species_ids: List[str]) -> pd.DataFrame:
    '''
    Searches POWO for species names which have a common names section.
    :param species_names:
    :param species_ids:
    :param output_csv:
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
                out_dict['Source'].append('POWO pages:' + str(id))
        except HTTPError:
            print(f'Couldnt find id: {species_ids[i]}')
    df = pd.DataFrame(out_dict)

    df.to_csv(powo_common_names_temp_output_csv)
    return df


def get_wiki_common_names(species_names: List[str]):
    wikipedia_searches.search_for_common_names(species_names, wiki_common_names_temp_output_csv)


def standardise_names():
    # standardise_names_in_column('Name', wiki_common_names_temp_output_csv)
    # standardise_names_in_column('Name', powo_common_names_temp_output_csv)

    # R imports col names with spaces as full stops
    # This need batching
    standardise_names_in_column('Scientific.Name.with.Author', cleaned_USDA_csv)


def compile_all_hits(output_csv: str) -> pd.DataFrame:
    usda_hits = get_UDSA_info()
    spp_ppa_df = get_common_names_spp_ppa()
    powo_hits = pd.read_csv(powo_common_names_temp_output_csv)
    wiki_hits = pd.read_csv(wiki_common_names_temp_output_csv)

    all_dfs = [usda_hits, powo_hits, wiki_hits, spp_ppa_df]
    for df in all_dfs:
        cols_to_drop = [c for c in df.columns if
                        c not in ['ID', 'Accepted_Name', 'Snippet', 'POWO_Snippet', 'PPA_Snippet', 'SPP_Snippet',
                                  'USDA_Snippet', 'Wiki_Snippet', 'Source']]
        df.drop(columns=cols_to_drop, inplace=True)

    merged_usda_powo = pd.merge(usda_hits, powo_hits, on="Accepted_Name", how="outer")
    merged = pd.merge(merged_usda_powo, wiki_hits, on="Accepted_Name", how="outer")

    merged = pd.concat([merged, spp_ppa_df])
    merged.set_index('Accepted_Name', inplace=True)
    merged.rename(columns={}, inplace=True)

    # Merge Sources:
    sources_cols = ['Source_y', 'Source_x', 'Source']
    for col in sources_cols:
        merged[col] = merged[col].astype('string')
        merged[col] = merged[col].fillna('')
    merged.to_csv(output_csv)
    merged['Sources'] = merged[sources_cols].agg(':'.join, axis=1)
    merged.drop(columns=sources_cols, inplace=True)

    merged.to_csv(output_csv)
    return merged


# TODO: get IDs from accepted names and merge on IDs

def main():
    # species_data = pd.read_csv("../temp_outputs/clean.csv")
    # species_data.set_index('Accepted_Name', inplace=True)
    # clean_usda_names()

    # species_list = species_data.index
    #
    # wikipedia_searches.search_for_common_names(species_list, 'temp_outputs/wiki_common_name_hits.csv')

    # get_powo_pages(species_list, species_data['Accepted_ID'].values, )

    # get_UDSA_info('temp_outputs/USDA_common_name_hits.csv')

    # compile_all_hits('outputs/list_of_plants_with_common_names.csv')
    # get_common_names_from_powo_files()
    standardise_names()
    # clean_usda_names()


if __name__ == '__main__':
    main()
