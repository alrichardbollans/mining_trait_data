import string
import pandas as pd
import requests
from typing import List
from tqdm import tqdm
import wikipediaapi


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


def make_wiki_hit_df(species_list: List[str], output_csv: str) -> pd.DataFrame:
    out_dict = {'Accepted_Name': [], 'Language': []}
    languages_to_check = ['es', 'en', 'fr', 'it', 'pt']
    wikis_to_check = [wikipediaapi.Wikipedia(lan) for lan in languages_to_check]
    for i in tqdm(range(len(species_list)), desc="Searching…", ascii=False, ncols=72):
        sp = species_list[i]
        language_hits = []
        for wiki in wikis_to_check:

            if check_page_exists(sp, wiki):
                language_hits.append(wiki.language)

        if len(language_hits) > 0:
            out_dict['Language'].append(str(language_hits))
            out_dict['Accepted_Name'].append(sp)


    df = pd.DataFrame(out_dict)
    df.to_csv(output_csv)
    return df
