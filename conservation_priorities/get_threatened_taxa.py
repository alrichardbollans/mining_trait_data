import os

import requests
from typing import List
import pandas as pd
from pkg_resources import resource_filename

from taxa_lists import get_all_taxa


_outputs_path = resource_filename(__name__, 'outputs')
rub_apoc_threatened_csv = os.path.join(_outputs_path, 'rub_apocs_threatened.csv')

def get_threatened_taxa_in_genus(genus,family:str=None)->pd.DataFrame:
    # Note by default we don't search by family as families are commonly not given in the bgci data
    # If it is important that genera with the sames from other families aren't included you can specify the family of interest
    _base_url = 'https://tools.bgci.org/export_threatsearch.php?ftrFamily=FAMILY&ftrGenus=GENUS&ftrSpecies=&ftrInfraSpecName=&ftrBGCI_Scope=&ftrAssessmentYear=&ftrThreatened=Threatened&ftrPagerLimit=100000&action=Find&export=1'
    url_format = _base_url.replace('GENUS', genus)
    if family is not None:
        url_format = _base_url.replace('FAMILY', family)
    return pd.read_csv(url_format)

def get_threatened_taxa_in_family(families :List[str])->pd.DataFrame:
    taxa = get_all_taxa(families_of_interest=families, accepted=True)
    genera_dfs = []
    for genus in taxa['genus'].unique().values:
        genera_dfs.append(get_threatened_taxa_in_genus(genus))

    return pd.concat(genera_dfs)



def main():
    get_threatened_taxa_in_family(['Apocynaceae', 'Rubiaceae']).to_csv(rub_apoc_threatened_csv)
if __name__ == '__main__':
    main()
