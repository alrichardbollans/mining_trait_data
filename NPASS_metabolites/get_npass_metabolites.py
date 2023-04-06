def get_npass_metabolites():
    import os.path

    import pandas as pd
    from pkg_resources import resource_filename
    from wcvp_name_matching import get_accepted_info_from_names_in_column

    _inputs_path = resource_filename(__name__, 'inputs')

    np_sp_pairs = pd.read_csv(
        os.path.join(_inputs_path, 'NPASSv2.0_download_naturalProducts_species_pair.txt')
        , sep='\t')[['org_id', 'np_id']]

    np_input = pd.read_csv(os.path.join(_inputs_path, 'NPASSv2.0_download_naturalProducts_generalInfo.txt'),
                           sep='\t')[['np_id', 'pref_name']]

    sp_input = pd.read_csv(os.path.join(_inputs_path, 'NPASSv2.0_download_naturalProducts_speciesInfo.txt'),
                           sep='\t')[['kingdom_name', 'org_id', 'org_name']]
    sp_input = sp_input[sp_input['kingdom_name'] == 'Viridiplantae']
    species_with_np_info = pd.merge(np_sp_pairs, np_input, on='np_id', how='left')
    species_with_info = pd.merge(species_with_np_info, sp_input, on='org_id', how='inner')
    species_with_info['org_name'] = species_with_info['org_name'].str.replace('0', 'No')

    acc_species_with_info = get_accepted_info_from_names_in_column(species_with_info, 'org_name')
    acc_species_with_info['Source'] = 'NPASS'
    return acc_species_with_info
