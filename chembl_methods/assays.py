import os

import pandas as pd
from pkg_resources import resource_filename

_output_path = resource_filename(__name__, 'outputs')


def get_compound_info_from_chembl_apm_assays():
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
        df.to_csv(os.path.join(_output_path, 'chembl_apm_compounds.csv'))


if __name__ == '__main__':
    get_compound_info_from_chembl_apm_assays()
