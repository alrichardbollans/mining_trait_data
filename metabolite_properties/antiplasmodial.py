import os

import pandas as pd
from pkg_resources import resource_filename
from wcvp_download import wcvp_accepted_columns

from knapsack_searches import kn_metabolite_name_column

_inputs_path = resource_filename(__name__, 'inputs')


def simplify_inchi_key(inch: str):
    if inch == inch:
        return inch[:14]
    else:
        return inch


def get_knapsack_antimalarial_metabolites():
    # From http://www.knapsackfamily.com/MetaboliteActivity/result.php 'malaria'

    with open(os.path.join(_inputs_path, 'knapsackantimalarialmetabolites.html'), "r") as f:
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
    with open(os.path.join(_inputs_path, 'knapsackantimalarialmetabolites.html'), "r") as f:
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


def get_compound_info_from_chembl_apm_assays(out_path: str):
    # THis needs manually reviewing e.g.
    # https://www.ebi.ac.uk/chembl/g/#browse/activities/full_state/eyJsaXN0Ijp7InNldHRpbmdzX3BhdGgiOiJFU19JTkRFWEVTX05PX01BSU5fU0VBUkNILkFDVElWSVRZIiwiY3VzdG9tX3F1ZXJ5IjoiYXNzYXlfY2hlbWJsX2lkOkNIRU1CTDc2Mjk5MCIsInVzZV9jdXN0b21fcXVlcnkiOnRydWUsInNlYXJjaF90ZXJtIjoiIiwidGV4dF9maWx0ZXIiOiJDSEVNQkwxMTEwNzYifX0%3D
    # Is counted as active, but the ic50 value is Concentration required to reduce chloroquine IC50 by 50%
    compound_data = []
    from chembl_webresource_client.new_client import new_client
    target = new_client.target

    pf = target.filter(pref_name__startswith='Plasmodium ').only('organism', 'target_chembl_id')

    for p_sp in pf:
        organism = p_sp['organism']
        activity = new_client.activity
        pf_activities = activity.filter(target_chembl_id=p_sp['target_chembl_id'],
                                        pchembl_value__isnull=False,  # has some value
                                        # pchembl_value__gte=6  #See https://chembl.gitbook.io/chembl-interface-documentation/frequently-asked-questions/chembl-data-questions
                                        # pChEMBL is defined as: -Log(molar IC50, XC50, EC50, AC50, Ki, Kd or Potency).
                                        # pIC50 value for IC50 < 1μM is 6
                                        # This condition ensures that only compounds with a pIC50 value (the negative logarithm of IC50)
                                        # greater than or equal to 6 (corresponding to IC50 <= 1μM) are retrieved.
                                        ).only('molecule_chembl_id', 'pchembl_value', 'standard_type', 'standard_units', 'standard_value',
                                               'assay_chembl_id')

        # Download the compounds and collect data
        from tqdm import tqdm
        for i in tqdm(range(len(pf_activities)), desc=f'Getting compounds for {organism}', ascii=False, ncols=172):

            compound_activity = pf_activities[i]
            molecule_id = compound_activity['molecule_chembl_id']
            pchembl_value = compound_activity['pchembl_value']
            standard_type = compound_activity['standard_type']
            standard_units = compound_activity['standard_units']
            standard_value = compound_activity['standard_value']
            assay_chembl_id = compound_activity['assay_chembl_id']

            # Get compound details
            compound_details = new_client.molecule.get(molecule_id)
            inchikey = None
            smiles = None
            if compound_details['molecule_structures'] is not None:
                inchikey = compound_details['molecule_structures']['standard_inchi_key']
                smiles = compound_details['molecule_structures']['canonical_smiles']
            name = compound_details['pref_name']
            compound_data.append(
                {'Compound_Name': name, 'assay_standard_value': standard_value, 'assay_standard_units': standard_units,
                 'assay_standard_type': standard_type, 'assay_pchembl_value': pchembl_value, 'target_organism': organism,
                 'assay_chembl_id': assay_chembl_id,
                 'InChIKey': inchikey, 'Smiles': smiles,
                 'molecule_chembl_id': molecule_id, 'natural_product': compound_details['natural_product']})

        # Create a DataFrame from the compound data
        df = pd.DataFrame(compound_data).drop_duplicates(keep='first').reset_index(drop=True)
        df.to_csv(out_path)
        return df
