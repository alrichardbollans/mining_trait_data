import requests
from typing import List
import pandas as pd
test_url ='https://tools.bgci.org/export_threatsearch.php?ftrFamily=&ftrGenus=Aspidosperma&ftrSpecies=&ftrInfraSpecName=&ftrBGCI_Scope=&ftrAssessmentYear=&ftrThreatened=Threatened&ftrPagerLimit=100000&action=Find&export=1'

base_url = 'https://tools.bgci.org/export_threatsearch.php?ftrFamily=&ftrGenus=GENUS&ftrSpecies=&ftrInfraSpecName=&ftrBGCI_Scope=&ftrAssessmentYear=&ftrThreatened=Threatened&ftrPagerLimit=100000&action=Find&export=1'

def get_threatened_taxa_in_genus(genus):
    url_format = base_url.replace('GENUS',genus)
    p= pd.read_csv(url_format)
    pass

def get_threatened_taxa(taxa_list :List[str],):
    pass


def main():
    get_threatened_taxa_in_genus('Aspidosperma')
if __name__ == '__main__':
    main()
