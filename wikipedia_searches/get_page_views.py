from typing import List
import pandas as pd
from tqdm import tqdm


def get_project_from_language(lan: str):
    return lan + '.wikipedia.org'


def get_request_url_for_taxon(taxon: str, lan: str) -> str:
    """
    Gets the url to request to wikimedia api.
    Currently set to get USER views for range 2017-04-01 -> 2022-04-01
    :param taxon:
    :param lan:
    :return:
    """

    import wikipediaapi
    import time
    import urllib.parse

    if lan == 'zh':
        wiki_lan = wikipediaapi.Wikipedia('en')
        time.sleep(.01)
        page_py = wiki_lan.page(taxon)
        try:
            formatted_title = urllib.parse.quote(page_py.langlinks['zh'].title)
        except KeyError:
            return ''
    else:
        wiki_lan = wikipediaapi.Wikipedia(lan)
        time.sleep(.01)
        page_py = wiki_lan.page(taxon)
        formatted_title = urllib.parse.quote(page_py.title)
    project = get_project_from_language(lan)
    req_url = 'https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/' + project + '/all-access/user/' + formatted_title + '/monthly/20170401/20220401'
    return req_url


def get_page_views_for_taxon_in_lan(taxon: str, lan: str):
    import time
    import requests

    taxon_url = get_request_url_for_taxon(taxon, lan)
    if taxon_url == '':
        return 0, 0
    headers = {'User-Agent': 'TraitBot/0.0 (a.richard-bollans@kew.org)'}
    resp = requests.get(taxon_url, headers=headers)
    # Avoid rate limiting (100 req/s)
    time.sleep(.01)
    data = resp.json()

    total_views = 0
    num_months = 0
    try:
        for item in data['items']:
            num_months += 1
            total_views += item['views']
    except KeyError:
        total_views = 0
        num_months = 0

    return float(total_views), num_months


def get_all_page_views_for_taxon(taxon: str):
    languages_to_check = ['es', 'en', 'fr', 'it', 'pt', 'zh']
    count = 0

    total_num_months = 0
    for lan in languages_to_check:
        lan_count, num_months = get_page_views_for_taxon_in_lan(taxon, lan)
        count += lan_count
        total_num_months += num_months
    if total_num_months == 0:
        return 0
    else:
        avg_month_count = float(count) / total_num_months

    return avg_month_count


def make_pageview_df(taxa_list: List[str], output_csv: str):
    from wcvpy.wcvp_name_matching import get_accepted_info_from_names_in_column

    out_dict = {'name': [], 'Wikipedia_PageViews': []}

    for i in tqdm(range(len(taxa_list)), desc="Getting pageviews", ascii=False, ncols=72):
        sp = taxa_list[i]
        out_dict['name'].append(sp)
        x = get_all_page_views_for_taxon(sp)
        out_dict['Wikipedia_PageViews'].append(x)

    df = pd.DataFrame(out_dict)
    acc_df = get_accepted_info_from_names_in_column(df, 'name')

    acc_df.to_csv(output_csv)

