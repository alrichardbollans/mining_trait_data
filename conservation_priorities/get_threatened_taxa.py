import os

import requests
from typing import List
import pandas as pd
from pkg_resources import resource_filename

from taxa_lists import get_all_taxa
from automatchnames import get_accepted_info_from_names_in_column
from tqdm import tqdm

_outputs_path = resource_filename(__name__, 'outputs')
rub_apoc_threatened_csv = os.path.join(_outputs_path, 'rub_apocs_threatened.csv')
rub_apoc_accepted_threatened_csv = os.path.join(_outputs_path, 'rub_apocs_accepted_threatened.csv')


def get_threatened_taxa_in_genus(genus, family: str = '') -> pd.DataFrame:
    # Note by default we don't search by family as families are commonly not given in the bgci data
    # If it is important that genera with the sames from other families aren't included you can specify the family of interest
    _base_url = 'https://tools.bgci.org/export_threatsearch.php?ftrFamily=FAMILY&ftrGenus=GENUS&ftrSpecies=&ftrInfraSpecName=&ftrBGCI_Scope=&ftrAssessmentYear=&ftrThreatened=Threatened&ftrPagerLimit=100000&action=Find&export=1'
    url_format = _base_url.replace('GENUS', genus)
    url_format = url_format.replace('FAMILY', family)
    return pd.read_csv(url_format)


def get_threatened_taxa_in_family(families: List[str]) -> pd.DataFrame:
    taxa = get_all_taxa(families_of_interest=families, accepted=True)
    genera_dfs = []
    for i in tqdm(range(len(taxa['genus'].unique().tolist())), desc="Searching…", ascii=False, ncols=72):
        genus = taxa['genus'].unique().tolist()[i]
        genera_dfs.append(get_threatened_taxa_in_genus(genus))

    return pd.concat(genera_dfs)


def get_accepted_info_for_taxa_in_csv(in_csv: str, output_csv: str, families=None):
    threatened = pd.read_csv(in_csv)
    db_acc = get_accepted_info_from_names_in_column(threatened, 'Plant Name', families_of_interest=families)
    db_acc.to_csv(output_csv)


def main():
    fams = ['Apocynaceae', 'Rubiaceae']
    # get_threatened_taxa_in_family(fams).to_csv(rub_apoc_threatened_csv)
    get_accepted_info_for_taxa_in_csv(rub_apoc_threatened_csv, rub_apoc_accepted_threatened_csv, families=fams)


if __name__ == '__main__':
    main()
