import os

from pkg_resources import resource_filename

_inputs_path = resource_filename(__name__, 'inputs')


def dig_into_kegg_dicts(compound_list, d):
    if 'children' in d.keys():
        for child in d['children']:
            dig_into_kegg_dicts(compound_list, child)
    else:
        compound_list.append(d['name'])


def get_alkaloids_from_kegg_brite():
    import json
    # See e.g. https://www.genome.jp/kegg-bin/get_htext?br08003.keg
    input_json = os.path.join(_inputs_path, 'keggbr08003.json')
    alks = []
    # JSON file
    f = open(input_json, "r")
    compounds = json.load(f)

    alkaloids_dict = compounds["children"][0]

    dig_into_kegg_dicts(alks, alkaloids_dict)

    f.close()

    return alks



def get_steroids_from_kegg_brite():
    import json
    # See e.g. https://www.genome.jp/brite/br08003
    input_json = os.path.join(_inputs_path, 'keggbr08003.json')
    steroids = []
    # JSON file
    f = open(input_json, "r")
    compounds = json.load(f)

    steroids_dict = compounds["children"][4]['children'][6]

    dig_into_kegg_dicts(steroids, steroids_dict)

    f.close()

    return steroids


def get_cardenolides_from_kegg_brite():
    import json
    # Note cardenolides are misspelt as Cardanolides in keggbrite
    # See e.g. https://www.genome.jp/brite/br08003
    input_json = os.path.join(_inputs_path, 'keggbr08003.json')
    cards = []
    # JSON file
    f = open(input_json, "r")
    compounds = json.load(f)

    card_dict = compounds["children"][4]['children'][6]['children'][3]

    dig_into_kegg_dicts(cards, card_dict)
    f.close()

    return cards

