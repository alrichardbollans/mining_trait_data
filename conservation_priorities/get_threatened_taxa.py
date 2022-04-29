import os

import requests
from typing import List
import pandas as pd
from pkg_resources import resource_filename

from taxa_lists import get_all_taxa
from automatchnames import get_accepted_info_from_names_in_column
from tqdm import tqdm

_temp_outputs_path = resource_filename(__name__, 'temp_outputs')
rub_apoc_threat_status_csv = os.path.join(_temp_outputs_path, 'rub_apoc_threat_status.csv')

_outputs_path = resource_filename(__name__, 'outputs')

rub_apoc_accepted_threat_status_csv = os.path.join(_outputs_path, 'rub_apoc_accepted_threat_status.csv')


def get_threat_status_for_taxa_in_genus(genus, family: str = '') -> pd.DataFrame:
    # Note by default we don't search by family as families are commonly not given in the bgci data
    # If it is important that genera with the same names from other families aren't included you can specify the family of interest
    _base_url = 'https://tools.bgci.org/export_threatsearch.php?ftrFamily=FAMILY&ftrGenus=GENUS&ftrSpecies=&ftrInfraSpecName=&ftrBGCI_Scope=&ftrAssessmentYear=&ftrThreatened=&ftrPagerLimit=100000&action=Find&export=1'
    url_format = _base_url.replace('GENUS', genus)
    url_format = url_format.replace('FAMILY', family)
    return pd.read_csv(url_format)


def get_threat_status_taxa_in_family(families: List[str], temp_output_csv: str, output_csv: str,
                                     ranks: List[str] = None) -> pd.DataFrame:
    if ranks is not None:
        taxa = get_all_taxa(families_of_interest=families, accepted=True, ranks=ranks)
    else:
        taxa = get_all_taxa(families_of_interest=families, accepted=True)

    genera_dfs = []
    for i in tqdm(range(len(taxa['genus'].unique().tolist())), desc="Searching…", ascii=False, ncols=72):
        genus = taxa['genus'].unique().tolist()[i]
        genera_dfs.append(get_threat_status_for_taxa_in_genus(genus))

    all_genera_df = pd.concat(genera_dfs)
    all_genera_df = all_genera_df[all_genera_df['Family'].isin(families) | all_genera_df['Family'].isna()]
    all_genera_df.to_csv(temp_output_csv)

    accepted = get_accepted_info_from_names_in_column(all_genera_df, 'Plant Name', families_of_interest=families)

    accepted.to_csv(output_csv)
    return all_genera_df


def _get_accepted_info_for_taxa_in_csv(in_csv: str, output_csv: str, families=None):
    threatened = pd.read_csv(in_csv)
    db_acc = get_accepted_info_from_names_in_column(threatened, 'Plant Name', families_of_interest=families)
    db_acc.to_csv(output_csv)


def interpret_status(threat_df: pd.DataFrame):
    # With same species and different status
    # Prioritise global scope and then prioritise year

    taxa_df = get_all_taxa(families_of_interest=threat_df['Family'].values.tolist(), accepted=True, ranks=['Species'])

    for i in tqdm(range(len(taxa_df['accepted_name'].unique().tolist())), desc="Searching…", ascii=False, ncols=72):
        species = taxa_df['accepted_name'].unique().tolist()[i]
        sp_threats = threat_df[threat_df['Accepted_Species'] == species]
        if len(sp_threats['Interpreted Conservation Status'].unique()) > 1:
            print('########')
            print(species)
            print(sp_threats['Interpreted Conservation Status'].unique())
