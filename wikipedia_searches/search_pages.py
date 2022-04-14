import hashlib
import os
import urllib.parse
import string
import pandas as pd
import requests
from typing import List

from pkg_resources import resource_filename
from tqdm import tqdm
import wikipediaapi

from automatchnames import get_accepted_info_from_names_in_column

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


def get_page_url_from_title(lang: str, title: str):
    t = urllib.parse.quote(title)
    return 'https://' + lang + '.wikipedia.org/wiki/' + t


def search_for_poisons(output_csv: str) -> pd.DataFrame:
    # First get english data
    en_tables = pd.read_html('https://en.wikipedia.org/wiki/List_of_poisonous_plants')
    scientific_names = {'name': [], 'Source': []}

    def append_to_scientific_names(values: List[str], source: str):
        for x in values:
            if x not in scientific_names['name']:
                scientific_names['name'].append(x)
                scientific_names['Source'].append(source)
            else:
                i = scientific_names['name'].index(x)
                scientific_names['Source'][i] += ':' + source

    append_to_scientific_names(en_tables[0]['Scientific name'].values.tolist(), 'en_wiki')
    append_to_scientific_names(en_tables[1]['Scientific name'].values.tolist(), 'en_wiki')

    en_wiki = wikipediaapi.Wikipedia('en')
    p = en_wiki.page('List_of_poisonous_plants')

    # Then check linked languages
    langs_to_check = p.langlinks

    # Info on which tables from the page to use and the column name of the scientific name
    # Not this misses some pages which aren't easily parsed
    table_info = {'an': [[0, 'বৈজ্ঞানিক নাম']], 'bn': [[0, 'বৈজ্ঞানিক নাম']], 'cs': [[0, 'Český název']],
                  'de': [[0, 'Wissenschaftlicher Name']], 'fr': [[0, 'Nom scientifique']],
                  'hr': [[0, 'Znanstveni naziv']], 'hu': [[2, 'Latin név']]}

    for l in langs_to_check:
        if l in table_info:

            url = get_page_url_from_title(l, langs_to_check[l].title)

            r = requests.get(url)
            website = r.text
            tables = pd.read_html(website, encoding='utf-8')
            for pair in table_info[l]:
                append_to_scientific_names(tables[pair[0]][pair[1]].values.tolist(), l + '_wiki')

    wiki_poisons_df = pd.DataFrame(scientific_names)
    dup_names = wiki_poisons_df[wiki_poisons_df.duplicated(subset=['name'])]
    if len(dup_names.index) > 0:
        print(dup_names)
        raise ValueError('Incorrectly merged wiki name')
    wiki_poisons_df.to_csv(output_csv)
    return wiki_poisons_df


def search_for_common_names(taxa_list: List[str], output_csv: str) -> pd.DataFrame:
    if output_csv is not None:
        if not os.path.isdir(os.path.dirname(output_csv)):
            os.mkdir(os.path.dirname(output_csv))
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
    for sp in taxa_list:

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


def check_page_exists(taxon: str, wiki_lan: wikipediaapi.Wikipedia) -> bool:
    page_py = wiki_lan.page(taxon)
    if page_py.exists():
        return True
    else:
        return False


def make_wiki_hit_df(taxa_list: List[str], output_csv: str = None, force_new_search=False) -> pd.DataFrame:
    if output_csv is not None:
        if not os.path.isdir(os.path.dirname(output_csv)):
            os.mkdir(os.path.dirname(output_csv))
    name_col = 'Name'
    out_dict = {name_col: [], 'Language': []}
    languages_to_check = ['es', 'en', 'fr', 'it', 'pt', 'zh']
    wikis_to_check = [wikipediaapi.Wikipedia(lan) for lan in languages_to_check]
    # Save previous searches using a hash of names to avoid repeating searches
    names = list(taxa_list)
    str_to_hash = str(names).encode()
    temp_csv = "wiki_page_search_" + str(hashlib.md5(str_to_hash).hexdigest()) + ".csv"

    temp_output_wiki_page_csv = os.path.join(_temp_outputs_path, temp_csv)
    unchecked_taxa_due_to_timeout = []
    if os.path.isfile(temp_output_wiki_page_csv) and not force_new_search:

        df = pd.read_csv(temp_output_wiki_page_csv, index_col=0)
    else:

        for i in tqdm(range(len(taxa_list)), desc="Searching for Wiki Pages…", ascii=False, ncols=72):
            sp = taxa_list[i]
            language_hits = []
            try:
                for wiki in wikis_to_check:
                    if check_page_exists(sp, wiki):
                        language_hits.append(wiki.language)

                if len(language_hits) > 0:
                    out_dict['Language'].append(str(language_hits))
                    out_dict[name_col].append(sp)

            except:
                unchecked_taxa_due_to_timeout.append(sp)

        df = pd.DataFrame(out_dict)

    if len(unchecked_taxa_due_to_timeout) > 0:
        taxa_to_check_dict = {'taxa': unchecked_taxa_due_to_timeout}
        check_df = pd.DataFrame(taxa_to_check_dict)
        check_csv = os.path.join(_temp_outputs_path, 'taxa_to_recheck.csv')
        check_df.to_csv(check_csv)
        print(
            f'Warning {str(len(unchecked_taxa_due_to_timeout))} taxa were unchecked due to server timeouts. Rerun search for taxa in {check_csv}')

    df.to_csv(temp_output_wiki_page_csv)

    acc_df = get_accepted_info_from_names_in_column(df, name_col)

    acc_df.to_csv(output_csv)
    return acc_df


if __name__ == '__main__':
    clan = wikipediaapi.Wikipedia('zh')
    check_page_exists('Catharanthus roseus', clan)
    # search_for_poisons('test.csv')
