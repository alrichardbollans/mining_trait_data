import urllib.request
from urllib.error import HTTPError

import pandas as pd
from typing import List

import wikipedia_searches


def clean_usda_names():
    def first_cleaning(given_name: str) -> str:
        out = given_name.replace(' ×', ' ')
        return out

    def second_cleaning(given_name: str) -> str:
        out = given_name.replace('×', '')
        return out

    usda_df = pd.read_csv('inputs/USDA Plants Database.csv')
    usda_df['Scientific Name with Author'] = usda_df['Scientific Name with Author'].apply(first_cleaning)
    usda_df['Scientific Name with Author'] = usda_df['Scientific Name with Author'].apply(second_cleaning)

    usda_df.to_csv('inputs/USDA Plants Database_cleaned.csv')


def get_UDSA_info(output_csv: str) -> pd.DataFrame:
    # First add accepted names using KNMS (http://namematch.science.kew.org/csv)
    # Get expanded and data has a header
    # Need to clean the downloaded version first. Use 'USDA Plants Database_cleaned.csv' See above
    usda_df = pd.read_csv('inputs/USDA Plants Database_matched_1641569303504.csv', sep='\t')
    # Drop rows with NaN common names
    usda_df = usda_df.rename(columns={'Scientific Name': 'Accepted_Name', 'Common Name': 'Snippet'})
    usda_df = usda_df.dropna(subset=['Snippet'])
    usda_df = usda_df.dropna(subset=['Accepted_Name'])
    usda_df = usda_df[usda_df['Rank'] == 'SPECIES']
    usda_df['Source'] = 'USDA Plants Database'

    usda_df.drop(columns=['Symbol', 'Synonym Symbol'], inplace=True)

    print(usda_df)
    usda_df.to_csv(output_csv)
    return usda_df


def get_powo_pages(species_names: List[str], species_ids: List[str], output_csv: str) -> pd.DataFrame:
    out_dict = {'Accepted_Name': [], 'Snippet': [], 'Source': []}
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
                out_dict['Accepted_Name'].append(name)
                out_dict['Snippet'].append(snippet)
                out_dict['Source'].append('POWO:' + str(id))
        except HTTPError:
            print(f'Couldnt find id: {species_ids[i]}')
    df = pd.DataFrame(out_dict)
    df.to_csv(output_csv)
    return df


def compile_all_hits(output_csv: str) -> pd.DataFrame:
    usda_hits = pd.read_csv('temp_outputs/USDA_common_name_hits.csv')
    powo_hits = pd.read_csv('temp_outputs/powo_common_name_hits.csv')
    wiki_hits = pd.read_csv('temp_outputs/wiki_common_name_hits.csv')

    all_dfs = [usda_hits, powo_hits, wiki_hits]
    for df in all_dfs:
        cols_to_drop = [c for c in df.columns if c not in ['Accepted_Name', 'Snippet', 'Source']]
        df.drop(columns=cols_to_drop, inplace=True)

    merged = pd.merge(usda_hits, powo_hits, on="Accepted_Name", how="outer")
    merged = pd.merge(merged, wiki_hits, on="Accepted_Name", how="outer")
    merged.set_index('Accepted_Name', inplace=True)
    merged.rename(columns={'Snippet_x': 'USDA Snippet', 'Snippet_y': 'POWO Snippet', 'Source_y': 'POWO ID',
                           'Snippet': 'Wiki Snippet', 'Source': 'Wiki Page'}, inplace=True)
    merged.to_csv(output_csv)
    return merged


def main():
    species_data = pd.read_csv("../temp_outputs/clean.csv")
    species_data.set_index('Accepted_Name', inplace=True)
    clean_usda_names()

    species_list = species_data.index
    #
    # wikipedia_searches.search_for_common_names(species_list, 'temp_outputs/wiki_common_name_hits.csv')

    # get_powo_pages(species_list, species_data['Accepted_ID'].values, "temp_outputs/powo_common_name_hits.csv")

    # get_UDSA_info('temp_outputs/USDA_common_name_hits.csv')

    compile_all_hits('outputs/list_of_plants_with_common_names.csv')


if __name__ == '__main__':
    main()
