import os

import pandas as pd
from pkg_resources import resource_filename

from knapsack_searches import kn_metabolite_name_column

_inputs_path = resource_filename(__name__, 'inputs')


def get_antimalarial_metabolites():
    # From http://www.knapsackfamily.com/MetaboliteActivity/result.php 'malaria'

    with open(os.path.join(_inputs_path, 'antimalarialmetabolites.html'), "r") as f:
        page = f.read()

    replaced = page.replace('<br>', 'break_this_unq')
    antimal_table = \
        pd.read_html(replaced)[0]

    antimal_table = antimal_table[antimal_table['Biological Activity (Function)'] != 'Antimalarial inactive']
    antimal_table = antimal_table.dropna(subset=['Metabolite Name'])
    kn_antimalarial_metabolites = antimal_table['Metabolite Name'].unique().tolist()

    out_list = []
    for m in kn_antimalarial_metabolites:
        if 'break_this_unq' in m:
            split_metabolites = m.split('break_this_unq')
            out_list += split_metabolites
        else:
            out_list.append(m)

    return out_list


def get_antimalarial_metabolite_hits_for_taxa(taxa_metabolite_data: pd.DataFrame, metabolite_col: str = None,
                                              output_csv: str = None) -> pd.DataFrame:
    """

    :param taxa_metabolite_data: from get_metabolites_in_family
    :param output_csv:
    :return:
    """
    antimal_metabolites = get_antimalarial_metabolites()
    if metabolite_col is None:
        metabolite_col = kn_metabolite_name_column
    anti_mal_taxa = taxa_metabolite_data[
        taxa_metabolite_data[metabolite_col].isin(antimal_metabolites)]
    if output_csv is not None:
        anti_mal_taxa.to_csv(output_csv)
    return anti_mal_taxa


def get_inactive_antimalarial_metabolites():
    # From http://www.knapsackfamily.com/MetaboliteActivity/result.php 'malaria'
    with open(os.path.join(_inputs_path, 'antimalarialmetabolites.html'), "r") as f:
        page = f.read()

    replaced = page.replace('<br>', 'break_this_unq')
    antimal_table = \
        pd.read_html(replaced)[0]
    print(antimal_table['Biological Activity (Function)'].unique())
    antimal_table = antimal_table[antimal_table['Biological Activity (Function)'] == 'Antimalarial inactive']
    antimal_table = antimal_table.dropna(subset=['Metabolite Name'])
    kn_metas = antimal_table['Metabolite Name'].unique().tolist()

    out_list = []
    for m in kn_metas:
        if 'break_this_unq' in m:
            split_metabolites = m.split('break_this_unq')
            out_list += split_metabolites
        else:
            out_list.append(m)

    return out_list


def get_inactive_antimalarial_metabolite_hits_for_taxa(taxa_metabolite_data: pd.DataFrame,
                                                       metabolite_col: str = None,
                                                       output_csv: str = None) -> pd.DataFrame:
    """

    :param taxa_metabolite_data: from get_metabolites_in_family
    :param output_csv:
    :return:
    """
    inactive_antimal_metabolites = get_inactive_antimalarial_metabolites()
    if metabolite_col is None:
        metabolite_col = kn_metabolite_name_column
    inactive_taxa = taxa_metabolite_data[
        taxa_metabolite_data[metabolite_col].isin(inactive_antimal_metabolites)]
    if output_csv is not None:
        inactive_taxa.to_csv(output_csv)

    return inactive_taxa


def get_manual_antimalarial_metabolite_hits_for_taxa(taxa_metabolite_data: pd.DataFrame,
                                                     metabolite_col: str = None,
                                                     output_csv: str = None) -> pd.DataFrame:
    """

    :param taxa_metabolite_data: from get_metabolites_in_family
    :param output_csv:
    :return:
    """
    # Metabolites from literature with activity <=1uM on any malaria strain
    # This is NOT EXHAUSTIVE
    # Contact package author for references
    # TODO: Make a file documenting these
    manual_known_antimal_metabolites = [x.lower() for x in
                                        ['Tubulosine', 'Emetine', 'Cephaeline', 'Artemether', 'Quinine',
                                         'Aspidocarpine', 'Cryptolepine', 'cryptoheptine',
                                         'Bisnicalaterine C', '10-hydroxy-ellipticin', 'tchibangensin',
                                         'ellipticin hydrochloride', 'usambarensin',
                                         '7S, 3S ochropposinine oxindole',
                                         'tetrahydro-4′,5′,6′,17-usambarensin 17S', '3,14-dihydro-ellipticin',
                                         '10-hydroxy-ellipticine', 'aplysinopsin',
                                         'Bisleucocurine', 'bisleucocurine A', 'anhydropereirine',
                                         'melohenine A', 'Artemisinin', 'Gedunin', 'Ulein', 'geissolosimine',
                                         'Voacamine', 'Ellipticine', 'Klugine', 'Longicaudatine Y',
                                         '16-Methoxyisomatopensine', 'Strychnopentamine',
                                         'Isostrychnopentamine', 'Alstonine', 'Himbeline',
                                         'Longicaudatine', 'Nicalaterine A', 'bisnicalaterine C',
                                         'Neosergeolide', '4-Nerolidylcatechol', 'Chloroquine',
                                         'Ochrolifuanine A', 'Strychnogucine B', 'leucoridine A N-oxide']]

    if metabolite_col is None:
        metabolite_col = kn_metabolite_name_column
    anti_mal_taxa = taxa_metabolite_data[
        taxa_metabolite_data[metabolite_col].str.lower().isin(manual_known_antimal_metabolites)]

    if output_csv is not None:
        anti_mal_taxa.to_csv(output_csv)

    return anti_mal_taxa
