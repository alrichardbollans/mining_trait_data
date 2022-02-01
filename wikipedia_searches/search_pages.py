import hashlib
import os
import string
import pandas as pd
import requests
from typing import List

from pkg_resources import resource_filename
from tqdm import tqdm
import wikipediaapi

_temp_outputs_path = resource_filename(__name__, 'temp_outputs')


def get_all_page_text(lang, pagename):
    response = requests.get('https://' + lang + '.wikipedia.org/w/api.php',
                            params={
                                'action': 'parse',
                                'format': 'json',
                                'page': pagename
                            }).json()
    try:
        # TODO: better catch this error, i.e. if response contains error
        text = next(iter(response['parse']['text'].values()))
    except KeyError:
        text = ""

    return text


def search_for_common_names(species_list: List[str], output_csv: str) -> pd.DataFrame:
    # TODO: also look for synonyms
    # Swedish list is split across the alphabet
    swedish_root_page = 'Lista_över_växter'
    swedish_alphabet = list(string.ascii_uppercase) + ['Å', 'Ä', 'Ö']
    swedish_titles = [swedish_root_page + '/' + a for a in swedish_alphabet]

    # Languages and associated pages of common plant name lists
    pagenames = {'en': ['List_of_plants_by_common_name'],
                 'als': ['Alemannische_Pflanzennamen_(Botanische_Namen)',
                         'Alemannische_Pflanzennamen_(nach_Systematik)',
                         'Alemannische_Pflanzennamen_(Deutsche_Namen)',
                         'Alemannische_Pflanzennamen_(nach_Dialekten)'],
                 'lb': ['Lëscht_vu_lëtzebuergesche_Planzennimm'],
                 'sv': swedish_titles,
                 'te': ['పుష్పాల_జాబితా'],
                 'chr': ['ᏗᎦᎪᏗ_ᏚᎾᏙᎥ_ᏙᎪᏪᎸ']
                 }

    page_texts = {}
    for lan in pagenames:
        for page in pagenames[lan]:
            source = lan + ": " + page

            page_texts[source] = get_all_page_text(lan, page)

    out_dict = {'Name': [], 'Wiki_Snippet': [], 'Source': []}
    for sp in species_list:

        try:
            hits = []
            snippets = []
            for source in page_texts:
                if sp in page_texts[source]:
                    hits.append(source)
                    i = page_texts[source].index(sp)
                    snippet = page_texts[source][i - 1:i + len(sp) + 1]
                    snippets.append(snippet)
            if len(hits) > 0:
                out_dict['Source'].append("Wiki (" + str(hits) + ")")
                out_dict['Wiki_Snippet'].append(str(snippets))
                out_dict['Name'].append(sp)

        except TypeError:
            pass

    df = pd.DataFrame(out_dict)
    df.to_csv(output_csv)
    return df


def check_page_exists(species: str, wiki_lan: wikipediaapi.Wikipedia) -> bool:
    page_py = wiki_lan.page(species)
    if page_py.exists():
        return True
    else:
        return False


def make_wiki_hit_df(species_list: List[str], force_new_search=False) -> pd.DataFrame:
    out_dict = {'Name': [], 'Language': []}
    languages_to_check = ['es', 'en', 'fr', 'it', 'pt']
    wikis_to_check = [wikipediaapi.Wikipedia(lan) for lan in languages_to_check]
    # Save previous searches using a hash of names to avoid repeating searches
    names = list(species_list)
    str_to_hash = str(names).encode()
    temp_csv = "wiki_page_search_" + str(hashlib.md5(str_to_hash).hexdigest()) + ".csv"

    temp_output_wiki_page_csv = os.path.join(_temp_outputs_path, temp_csv)
    unchecked_taxa_due_to_timeout = []
    if os.path.isfile(temp_output_wiki_page_csv) and not force_new_search:
        # Pandas will read TRUE/true as bools and therefore as True rather than true
        df = pd.read_csv(temp_output_wiki_page_csv)
    else:

        for i in tqdm(range(len(species_list)), desc="Searching…", ascii=False, ncols=72):
            sp = species_list[i]
            language_hits = []
            try:
                for wiki in wikis_to_check:
                    if check_page_exists(sp, wiki):
                        language_hits.append(wiki.language)

                if len(language_hits) > 0:
                    out_dict['Language'].append(str(language_hits))
                    out_dict['Name'].append(sp)

            except requests.exceptions.ReadTimeout:
                unchecked_taxa_due_to_timeout.append(sp)

        df = pd.DataFrame(out_dict)

    if len(unchecked_taxa_due_to_timeout) > 0:
        taxa_to_check_dict = {'taxa': unchecked_taxa_due_to_timeout}
        check_df = pd.DataFrame(taxa_to_check_dict)
        check_csv = os.path.join(_temp_outputs_path, 'taxa_to_recheck.csv')
        check_df.to_csv(check_csv)
        print(f'Warning some taxa were unchecked due to server timeouts. Rerun search for taxa in {check_csv}')

    df.to_csv(temp_output_wiki_page_csv)

    return df
