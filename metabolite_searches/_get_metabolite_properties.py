import os
import pandas as pd
import requests
from pkg_resources import resource_filename
from typing import List

from tqdm import tqdm

_inputs_path = resource_filename(__name__, 'inputs')

alkaloids_not_ending_in_ine = ['Kopsanone']
known_non_alkaloids = []

known_cardenolides_not_in_keggbrite = ['Acetyldigitoxin', 'Acetyldigoxin', 'Deslanoside', 'Digitoxigenin',
                                       'Digoxigenin', 'Gitoformate', 'Lanatoside C', 'Metildigoxin', 'Neoconvalloside',
                                       'k-Strophanthidin', 'Metildigoxin']


def get_antibacterial_metabolites():
    # From http://www.knapsackfamily.com/MetaboliteActivity/result.php 'antibacterial'
    antibac_table = pd.read_html(os.path.join(_inputs_path, 'antibacterialmetabolites.html'), flavor='html5lib')[0]
    antibac_table = antibac_table[antibac_table['Biological Activity (Function)'] != 'Antibacterial inactive']
    antibac_table = antibac_table.dropna(subset=['Metabolite Name'])
    return antibac_table['Metabolite Name'].unique().tolist()


def get_antimalarial_metabolites():
    # From http://www.knapsackfamily.com/MetaboliteActivity/result.php 'malaria'
    antimal_table = pd.read_html(os.path.join(_inputs_path, 'antimalarialmetabolites.html'), flavor='html5lib')[0]

    antimal_table = antimal_table[antimal_table['Biological Activity (Function)'] != 'Antimalarial inactive']
    antimal_table = antimal_table.dropna(subset=['Metabolite Name'])
    kn_antimalarial_metabolites = antimal_table['Metabolite Name'].unique().tolist()

    return kn_antimalarial_metabolites


def get_manual_antimalarial_metabolites():
    # Metabolites from literature with activity <=1uM on any malaria strain
    # This is NOT EXHAUSTIVE
    # Contact package author for references
    manual_known_antimal_metabolites = ['Tubulosine', 'Emetine', 'Cephaeline', 'Artemether', 'Quinine',
                                        'Aspidocarpine', 'Cryptolepine', 'Bisnicalaterine C', 'Bisleucocurine',
                                        'Voacamine', 'Ellipticine', 'Klugine', 'Longicaudatine Y',
                                        '16-Methoxyisomatopensine', 'Strychnopentamine', 'Isostrychnopentamine',
                                        'Longicaudatine', 'Ochrolifuanine A', 'Strychnogucine B']
    return manual_known_antimal_metabolites


def get_inactive_antimalarial_metabolites():
    # From http://www.knapsackfamily.com/MetaboliteActivity/result.php 'malaria'
    antimal_table = pd.read_html(os.path.join(_inputs_path, 'antimalarialmetabolites.html'), flavor='html5lib')[0]
    print(antimal_table['Biological Activity (Function)'].unique())
    antimal_table = antimal_table[antimal_table['Biological Activity (Function)'] == 'Antimalarial inactive']
    antimal_table = antimal_table.dropna(subset=['Metabolite Name'])
    return antimal_table['Metabolite Name'].unique().tolist()


def get_formulas_for_metabolite(metabolite: str):
    url_name_format = metabolite.replace(' ', '%20')
    url_name_format = url_name_format.replace('+', 'plus')
    url = f'http://www.knapsackfamily.com/knapsack_core/result.php?sname=metabolite&word={url_name_format}'
    try:

        tables = pd.read_html(url, flavor='html5lib')

    except UnicodeEncodeError:
        response = requests.get(url)
        decoded = response.content.decode()
        tables = pd.read_html(decoded, flavor='html5lib')
    meta_table = tables[0]
    try:
        formulas = meta_table['Molecular formula'].values.tolist()

        return formulas
    except (KeyError, IndexError):
        print(f'Warning: No info found for {metabolite}')
        return []


def dig_into_kegg_dicts(compound_list, d):
    if 'children' in d.keys():
        for child in d['children']:
            dig_into_kegg_dicts(compound_list, child)
    else:
        compound_list.append(d['name'])


def get_alkaloids_from_kegg_brite():
    import json
    # See e.g. https://www.genome.jp/brite/br08003
    input_json = os.path.join(_inputs_path, 'br08003.json')
    alks = []
    # JSON file
    f = open(input_json, "r")
    compounds = json.load(f)

    alkaloids_dict = compounds["children"][0]

    dig_into_kegg_dicts(alks, alkaloids_dict)

    return alks


def get_steroids_from_kegg_brite():
    import json
    # See e.g. https://www.genome.jp/brite/br08003
    input_json = os.path.join(_inputs_path, 'br08003.json')
    steroids = []
    # JSON file
    f = open(input_json, "r")
    compounds = json.load(f)

    steroids_dict = compounds["children"][4]['children'][6]

    dig_into_kegg_dicts(steroids, steroids_dict)

    return steroids


def get_cardenolides_from_kegg_brite():
    import json
    # Note cardenolides are misspelt as Cardanolides in keggbrite
    # See e.g. https://www.genome.jp/brite/br08003
    input_json = os.path.join(_inputs_path, 'br08003.json')
    cards = []
    # JSON file
    f = open(input_json, "r")
    compounds = json.load(f)

    card_dict = compounds["children"][4]['children'][6]['children'][3]

    dig_into_kegg_dicts(cards, card_dict)

    return cards


def get_alkaloids_from_metabolites(metabolites_to_check: List[str]) -> dict:
    """ Ends in 'ine' usually indicates alkaloid
        Must contain nitrogen
    """

    known_alkaloids = get_alkaloids_from_kegg_brite()

    alkaloid_metabolites = {'alks': [], 'Reason': []}
    suffixes = ["ine-", "ine ", "ine+", "ine("]

    for i in tqdm(range(len(metabolites_to_check)), desc="Searching for alks", ascii=False, ncols=72):
        m = metabolites_to_check[i]
        if any(alk in m for alk in alkaloids_not_ending_in_ine):
            alkaloid_metabolites['alks'].append(m)
            alkaloid_metabolites['Reason'].append('manual')
        elif any(m in alk for alk in known_alkaloids):
            alkaloid_metabolites['alks'].append(m)
            alkaloid_metabolites['Reason'].append('Kegg Brite')
            # print(f'{m} added from known_alkaloids')
        elif m not in known_non_alkaloids:
            if any(s in m for s in suffixes) or m.endswith('ine'):
                formulas = get_formulas_for_metabolite(m)
                if all("N" in f for f in formulas):
                    alkaloid_metabolites['alks'].append(m)
                    alkaloid_metabolites['Reason'].append('Contains Nitrogen and ine at end of word')

    return alkaloid_metabolites


def get_steroids_from_metabolites(metabolites_to_check: List[str]) -> dict:
    known_steroids = get_steroids_from_kegg_brite() + known_cardenolides_not_in_keggbrite

    steroid_metabolites = {'steroids': [], 'Reason': []}

    for i in tqdm(range(len(metabolites_to_check)), desc="Searching for steroids", ascii=False, ncols=72):
        m = metabolites_to_check[i]
        if any(m in steroid for steroid in known_steroids):
            steroid_metabolites['steroids'].append(m)
            steroid_metabolites['Reason'].append('Kegg Brite')

    return steroid_metabolites


def get_cardenolides_from_metabolites(metabolites_to_check: List[str]) -> dict:
    known_cards = get_cardenolides_from_kegg_brite() + known_cardenolides_not_in_keggbrite

    cardenolide_metabolites = {'cardenolides': [], 'Reason': []}

    for i in tqdm(range(len(metabolites_to_check)), desc="Searching for cardenolides", ascii=False, ncols=72):
        m = metabolites_to_check[i]
        if any(m in card for card in known_cards):
            cardenolide_metabolites['cardenolides'].append(m)
            cardenolide_metabolites['Reason'].append('Kegg Brite')

    return cardenolide_metabolites


if __name__ == '__main__':
    get_alkaloids_from_kegg_brite()
