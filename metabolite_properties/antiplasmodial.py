import os

import pandas as pd
import requests
from pkg_resources import resource_filename

from knapsack_searches import kn_metabolite_name_column
from wcvp_download import wcvp_accepted_columns

_inputs_path = resource_filename(__name__, 'inputs')
chembl_apm_compounds_csv = os.path.join(_inputs_path, 'chembl_apm_compounds.csv')


def get_knapsack_antimalarial_metabolites():
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


def get_knapsack_antimalarial_metabolite_hits_for_taxa(taxa_metabolite_data: pd.DataFrame,
                                                       metabolite_col: str,
                                                       output_csv: str = None) -> pd.DataFrame:
    """

    :param taxa_metabolite_data: from get_metabolites_in_family
    :param output_csv:
    :return:
    """
    antimal_metabolites = get_knapsack_antimalarial_metabolites()
    if metabolite_col is None:
        metabolite_col = kn_metabolite_name_column
    anti_mal_taxa = taxa_metabolite_data[
        taxa_metabolite_data[metabolite_col].isin(antimal_metabolites)]
    if output_csv is not None:
        anti_mal_taxa.to_csv(output_csv)
    return anti_mal_taxa


def get_knapsack_inactive_antimalarial_metabolites():
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


def get_knapsack_inactive_antimalarial_metabolite_hits_for_taxa(taxa_metabolite_data: pd.DataFrame,
                                                                metabolite_col: str,
                                                                output_csv: str = None) -> pd.DataFrame:
    """

    :param taxa_metabolite_data: from get_metabolites_in_family
    :param output_csv:
    :return:
    """
    inactive_antimal_metabolites = get_knapsack_inactive_antimalarial_metabolites()
    if metabolite_col is None:
        metabolite_col = kn_metabolite_name_column
    inactive_taxa = taxa_metabolite_data[
        taxa_metabolite_data[metabolite_col].isin(inactive_antimal_metabolites)]
    if output_csv is not None:
        inactive_taxa.to_csv(output_csv)

    return inactive_taxa


def get_manual_antimalarial_metabolite_hits_for_taxa(taxa_metabolite_data: pd.DataFrame,
                                                     CAS_ID_COL: str = None,
                                                     INCHIKEY_COL: str = None,
                                                     output_csv: str = None) -> pd.DataFrame:
    """

    :param taxa_metabolite_data: from get_metabolites_in_family
    :param output_csv:
    :return:
    """
    # Metabolites from literature with activity <=1uM on any malaria strain
    # This is NOT EXHAUSTIVE
    # Contact package author for references
    if CAS_ID_COL is None and INCHIKEY_COL is None:
        raise ValueError('Must specify one of CAS_ID_COL, INCHIKEY_COL')
    manual_apm_compounds_df = pd.read_excel(os.path.join(_inputs_path, 'APM Compounds.xlsx'))

    # Clean columns
    def clean_col(df, col):
        df[col] = df[col].str.strip()

    clean_col(manual_apm_compounds_df, 'CAS_ID')
    clean_col(manual_apm_compounds_df, 'InChIKey')

    def simplify_inchi_key(inch: str):
        if inch == inch:
            return inch[:14]
        else:
            return inch

    manual_apm_compounds_df['simple_inchi'] = manual_apm_compounds_df['InChIKey'].apply(simplify_inchi_key)

    if CAS_ID_COL is not None:
        clean_col(taxa_metabolite_data, CAS_ID_COL)
        manual_apm_compound_casids = manual_apm_compounds_df['CAS_ID'].dropna().values
        cas_id_antimal_taxa = taxa_metabolite_data[~taxa_metabolite_data[CAS_ID_COL].isna()]
        cas_id_antimal_taxa = cas_id_antimal_taxa[
            (cas_id_antimal_taxa[CAS_ID_COL].isin(manual_apm_compound_casids))]

    if INCHIKEY_COL is not None:
        clean_col(taxa_metabolite_data, INCHIKEY_COL)
        taxa_metabolite_data['simple_inchi_for_matching_apm'] = taxa_metabolite_data[INCHIKEY_COL].apply(simplify_inchi_key)

        inchi_antimal_taxa = taxa_metabolite_data[~taxa_metabolite_data['simple_inchi_for_matching_apm'].isna()]
        inchi_antimal_taxa = inchi_antimal_taxa[
            (inchi_antimal_taxa['simple_inchi_for_matching_apm'].isin(manual_apm_compounds_df['simple_inchi'].dropna().values))]

        taxa_metabolite_data = taxa_metabolite_data.drop(columns=['simple_inchi_for_matching_apm'])

    anti_mal_taxa = pd.concat([cas_id_antimal_taxa, inchi_antimal_taxa])
    anti_mal_taxa = anti_mal_taxa.drop_duplicates(subset=[wcvp_accepted_columns['name_w_author']])
    if output_csv is not None:
        anti_mal_taxa.to_csv(output_csv)

    return anti_mal_taxa
