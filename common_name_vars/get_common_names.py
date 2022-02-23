import hashlib
import os.path
import urllib.request
from urllib.error import HTTPError

import pandas as pd
from typing import List

from poison_vars import cornell_poison_file, CPCS_poison_file, UCANR_toxic_file, UCANR_nontoxic_file, usda_toxic_file, \
    tppt_toxic_file
from tqdm import tqdm

import wikipedia_searches
from pkg_resources import resource_filename

from cleaning import compile_hits, generic_prepare_data, get_tempout_csv

from automatchnames import get_accepted_info_from_names_in_column, clean_urn_ids, get_accepted_info_from_ids_in_column

### Inputs
from taxa_lists.get_taxa_from_wcvp import get_all_taxa

_inputs_path = resource_filename(__name__, 'inputs')
_inputs_species_path = resource_filename(__name__, '../inputs')
_input_species_csv = os.path.join(_inputs_species_path, 'standardised_order.csv')
_initial_USDA_csv = os.path.join(_inputs_path, 'USDA Plants Database.csv')
_initial_MPNS_csv = os.path.join(_inputs_path, 'MPNS V11 subset Apocynaceae + Rubiaceae.csv')
_ppa_africa_csv = os.path.join(_inputs_path, 'PPAfrica-botswana-commonnames', 'vernacularname.txt')
_species_profile_csv = os.path.join(_inputs_path, 'SpeciesProfileVernacular', 'vernacular.tab')

### Temp outputs
_temp_outputs_path = resource_filename(__name__, 'temp_outputs')

_wiki_common_names_temp_output_csv = os.path.join(_temp_outputs_path, 'wiki_common_name_hits.csv')
_powo_common_names_temp_output_csv = os.path.join(_temp_outputs_path, 'powo_common_name_hits.csv')

# Standardised versions
_spp_ppa_common_names_temp_output_accepted_csv = os.path.join(_temp_outputs_path, 'spp_ppa_common_names_accepted.csv')
_wiki_common_names_temp_output_accepted_csv = os.path.join(_temp_outputs_path, 'wiki_common_name_hits_accepted.csv')
_powo_common_names_temp_output_accepted_csv = os.path.join(_temp_outputs_path, 'powo_common_name_hits_accepted.csv')
_cleaned_USDA_accepted_csv = os.path.join(_temp_outputs_path, 'USDA Plants Database_cleaned_accepted.csv')
_cleaned_MPNS_accepted_csv = os.path.join(_temp_outputs_path, 'MPNS Data_cleaned_accepted.csv')

### Outputs
output_path = resource_filename(__name__, 'outputs')
output_common_names_csv = os.path.join(output_path, 'list_of_plants_with_common_names.csv')


def prepare_usda_common_names(families_of_interest=None):
    # # Copied from https://plants.usda.gov/csvdownload?plantLst=plantCompleteList
    usda_df = pd.read_csv(_initial_USDA_csv)
    usda_df.drop(columns=['Symbol', 'Synonym Symbol'], inplace=True)
    usda_df = usda_df.rename(columns={'Common Name': 'USDA_Snippet'})
    usda_df = usda_df.dropna(subset=['USDA_Snippet'])
    if families_of_interest is not None:
        usda_df = usda_df[usda_df['Family'].str.contains('|'.join(families_of_interest))]

    accepted_usda_df = get_accepted_info_from_names_in_column(usda_df, 'Scientific Name with Author')

    accepted_usda_df['Source'] = 'USDA Plants Database'

    accepted_usda_df.to_csv(_cleaned_USDA_accepted_csv)

    return accepted_usda_df


def prepare_common_names_spp_ppa() -> pd.DataFrame:
    # TODO: Note this data is not specific to any family
    species_profile = pd.read_csv(_species_profile_csv, sep='\t', header=None)

    species_profile['Source'] = 'SpeciesProfileVernacular'
    species_profile['SPP_Snippet'] = species_profile[1] + ":" + species_profile[2]
    species_profile['ID'] = species_profile[0].apply(clean_urn_ids)
    species_profile.drop(columns=[0, 1, 2, 3], inplace=True)

    ppa_africa = pd.read_csv(_ppa_africa_csv, sep='\t', header=None)
    ppa_africa['Source'] = 'PPAfrica-botswana-commonnames'
    ppa_africa['PPA_Snippet'] = ppa_africa[3] + ":" + ppa_africa[2]
    ppa_africa['ID'] = ppa_africa[0].apply(clean_urn_ids)
    ppa_africa.drop(columns=[0, 1, 2, 3, 4], inplace=True)

    merged = pd.merge(ppa_africa, species_profile, on="ID", how="outer")

    with_accepted_info = get_accepted_info_from_ids_in_column(merged, 'ID')

    with_accepted_info.to_csv(_spp_ppa_common_names_temp_output_accepted_csv)

    return with_accepted_info


def prepare_MPNS_common_names(families_of_interest: List[str] = None) -> pd.DataFrame:
    # TODO: Note this is particular to Rubiaceae and Apocynaceae
    # Requested from from MPNS
    mpns_df = pd.read_csv(_initial_MPNS_csv, header=1)
    mpns_df.drop(columns=['authority', 'plant_id'], inplace=True)

    mpns_df = mpns_df.dropna(subset=['non_sci_name'])
    mpns_df = mpns_df[mpns_df['non_sci_name_type'] == 'common']
    if families_of_interest is not None:
        mpns_df = mpns_df[mpns_df['family'].str.contains('|'.join(families_of_interest))]

    mpns_df['non_sci_name'] = mpns_df.groupby(['taxon_name'])['non_sci_name'].transform(lambda x: ':'.join(x))
    mpns_df = mpns_df.drop_duplicates()
    mpns_df.rename(columns={'non_sci_name': 'MPNS_Snippet'}, inplace=True)

    accepted_mpns_df = get_accepted_info_from_names_in_column(mpns_df, 'taxon_name',
                                                              families_of_interest=families_of_interest)

    accepted_mpns_df = accepted_mpns_df.dropna(subset=['Accepted_Name'])
    accepted_mpns_df['Source'] = 'MPNS'
    print(accepted_mpns_df)
    accepted_mpns_df.drop(accepted_mpns_df.columns[0], axis=1, inplace=True)

    accepted_mpns_df.to_csv(_cleaned_MPNS_accepted_csv)

    return accepted_mpns_df


def get_powo_common_names(species_names: List[str], species_ids: List[str],
                          families_of_interest: List[str] = None, force_new_search=False) -> pd.DataFrame:
    '''
    Searches POWO for species names which have a common names section.
    :param species_names:
    :param species_ids:
    :return:
    '''
    out_dict = {'Name': [], 'POWO_Snippet': [], 'Source': []}
    # Save previous searches using a hash of names to avoid repeating searches
    names = list(species_names)
    ids = list(species_ids)
    full_list = names + ids
    str_to_hash = str(full_list).encode()
    temp_csv = "powo_common_name_search_" + str(hashlib.md5(str_to_hash).hexdigest()) + ".csv"

    temp_output_powo_csv = os.path.join(_temp_outputs_path, temp_csv)
    if os.path.isfile(temp_output_powo_csv) and not force_new_search:

        df = pd.read_csv(temp_output_powo_csv)
    else:
        for i in tqdm(range(len(species_names)), desc="Searching POWO for common names…", ascii=False, ncols=72):
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
                    out_dict['Source'].append('POWO pages(' + str(id) + ')')
            except HTTPError:
                print(f'Couldnt find id on POWO: {species_ids[i]}')
        df = pd.DataFrame(out_dict)
    df.to_csv(temp_output_powo_csv)
    acc_df = get_accepted_info_from_names_in_column(df, 'Name',
                                                    families_of_interest=families_of_interest)

    acc_df.to_csv(_powo_common_names_temp_output_accepted_csv)
    return acc_df


def get_wiki_common_names(taxa_list: List[str], families_of_interest: List[str] = None):
    wiki_df = wikipedia_searches.search_for_common_names(taxa_list, _wiki_common_names_temp_output_csv)
    acc_wiki_df = get_accepted_info_from_names_in_column(wiki_df, 'Name',
                                                         families_of_interest=families_of_interest)
    acc_wiki_df.to_csv(_wiki_common_names_temp_output_accepted_csv)

    return acc_wiki_df


def prepare_cornell_data():
    tables = pd.read_html(cornell_poison_file)
    toxic_df = tables[0]
    generic_prepare_data('Cornell CALS', _temp_outputs_path, toxic_df, 'Scientific Name', dropifna=['Common Name(s)'])


def prepare_CPCS_data():
    tables = pd.read_html(CPCS_poison_file)

    non_toxic_db = tables[1]
    # Remove letter headers
    non_toxic_db = non_toxic_db[~non_toxic_db['Latin or scientific name'].str.contains('^[A-Z]$', regex=True)]
    generic_prepare_data('CPCS nontoxic', _temp_outputs_path, non_toxic_db, 'Latin or scientific name',
                         dropifna=['Common name'])

    toxic_db = tables[4]
    toxic_db = toxic_db[~toxic_db['Latin or scientific name'].str.contains('^[A-Z]$', regex=True)]
    generic_prepare_data('CPCS toxic', _temp_outputs_path, toxic_db, 'Latin or scientific name',
                         dropifna=['Common name'])


def prepare_toxic_UCANR_data():
    toxic_tables = pd.read_html(UCANR_toxic_file, header=0)
    toxic_db = toxic_tables[0]
    generic_prepare_data('UCANR Toxic', _temp_outputs_path, toxic_db, 'Toxic plants: Scientific name',
                         dropifna=['Common name'])


def prepare_nontoxic_UCANR_data():
    nontoxic_tables = pd.read_html(UCANR_nontoxic_file, header=0)
    nontoxic_db = nontoxic_tables[0]
    generic_prepare_data('UCANR NonToxic', _temp_outputs_path, nontoxic_db, 'Safe plants: Scientific name',
                         dropifna=['Common name'])


def prepare_duke_usda_data():
    cmmn_names = pd.read_csv(os.path.join(_inputs_path, 'COMMON_NAMES.csv'))
    taxa_codes = pd.read_csv(os.path.join(_inputs_path, 'FNFTAX.csv'))
    merged = pd.merge(cmmn_names, taxa_codes, on='FNFNUM')
    merged.dropna(subset=['CNNAM'], inplace=True)

    merged['Common names'] = merged.groupby(['TAXON'])['CNNAM'].transform(lambda x: ':'.join(x))
    merged = merged.drop_duplicates(subset=['TAXON'])

    generic_prepare_data('USDA(Duke)', _temp_outputs_path, merged, 'TAXON')


def prepare_TPPT_data():
    toxic_db = pd.read_csv(tppt_toxic_file)
    toxic_db.dropna(subset=['German_plant_name', 'English_plant_name'], how='all', inplace=True)
    generic_prepare_data('TPPT', _temp_outputs_path, toxic_db, 'Latin_plant_name',
                         families_of_interest=toxic_db['Plant_family'].unique().tolist())


def prepare_data():
    accepted_data = get_all_taxa(families_of_interest=['Apocynaceae', 'Rubiaceae'], accepted=True)

    ranks_to_use = ["Species", "Variety", "Subspecies"]

    accepted_taxa_df = accepted_data.loc[accepted_data["rank"].isin(ranks_to_use)]

    accepted_taxa = accepted_taxa_df["taxon_name"].values
    accepted_taxa_ids = accepted_taxa_df["kew_id"].values

    # Get lists
    get_wiki_common_names(accepted_taxa, families_of_interest=['Apocynaceae', 'Rubiaceae'])
    # # print('Finished getting wiki names')
    get_powo_common_names(accepted_taxa, accepted_taxa_ids, families_of_interest=['Apocynaceae', 'Rubiaceae'])

    prepare_usda_common_names(families_of_interest=['Apocynaceae', 'Rubiaceae'])
    prepare_common_names_spp_ppa()
    prepare_MPNS_common_names(families_of_interest=['Apocynaceae', 'Rubiaceae'])

    prepare_cornell_data()
    prepare_CPCS_data()
    prepare_toxic_UCANR_data()
    prepare_duke_usda_data()
    prepare_TPPT_data()


def main():
    if not os.path.isdir(_temp_outputs_path):
        os.mkdir(_temp_outputs_path)
    if not os.path.isdir(output_path):
        os.mkdir(output_path)

    # TODO: Note powo, wikipedia and USDA data is specific to our study
    # prepare_data()

    cornell_hits = pd.read_csv(get_tempout_csv('Cornell CALS', _temp_outputs_path))
    cpcs_hits = pd.read_csv(get_tempout_csv('CPCS nontoxic', _temp_outputs_path))
    cpcs_toxic_hits = pd.read_csv(get_tempout_csv('CPCS toxic', _temp_outputs_path))
    ucantoxic_hits = pd.read_csv(get_tempout_csv('UCANR Toxic', _temp_outputs_path))
    ucannontoxic_hits = pd.read_csv(get_tempout_csv('UCANR NonToxic', _temp_outputs_path))
    duke_hits = pd.read_csv(get_tempout_csv('USDA(Duke)', _temp_outputs_path))
    tppt_hits = pd.read_csv(get_tempout_csv('TPPT', _temp_outputs_path))

    usda_hits = pd.read_csv(_cleaned_USDA_accepted_csv)
    spp_ppa_df = pd.read_csv(_spp_ppa_common_names_temp_output_accepted_csv)
    powo_hits = pd.read_csv(_powo_common_names_temp_output_accepted_csv)
    wiki_hits = pd.read_csv(_wiki_common_names_temp_output_accepted_csv)
    mpns_hits = pd.read_csv(_cleaned_MPNS_accepted_csv)

    all_dfs = [mpns_hits, usda_hits, powo_hits, wiki_hits, spp_ppa_df, cornell_hits, cpcs_hits, cpcs_toxic_hits,
               ucantoxic_hits, ucannontoxic_hits, duke_hits, tppt_hits]
    compile_hits(all_dfs, output_common_names_csv)


if __name__ == '__main__':
    main()
