import os

import pandas as pd
from pkg_resources import resource_filename
from taxa_lists import get_all_taxa

from metabolite_searches import get_metabolites_for_taxa, output_alkaloids_from_metabolites, get_alkaloid_hits_for_taxa, \
    get_antibac_metabolite_hits_for_taxa, recheck_taxa

_output_path = resource_filename(__name__, 'outputs')

rubiaceae_apocynaceae_metabolites_output_csv = os.path.join(_output_path, 'rub_apocs_metabolites.csv')
_rubiaceae_apocynaceae_alks_output_csv = os.path.join(_output_path, 'rub_apocs_alkaloids.csv')
rub_apoc_alkaloid_hits_output_csv = os.path.join(_output_path, 'rub_apocs_alkaloid_hits.csv')
rub_apoc_antibac_metabolites_output_csv = os.path.join(_output_path, 'rub_apocs_antibac_metabolites.csv')
_check_output_csv = os.path.join(_output_path, 'rechecked_taxa.csv')

def get_rub_apoc_metabolites():
    data = get_all_taxa(families_of_interest=['Apocynaceae', 'Rubiaceae'], accepted=True)

    ranks_to_use = ["Species", "Variety", "Subspecies"]

    taxa = data.loc[data["rank"].isin(ranks_to_use)]

    taxa_list = taxa["taxon_name"].values

    get_metabolites_for_taxa(taxa_list, output_csv=rubiaceae_apocynaceae_metabolites_output_csv)

def get_rub_apoc_alkaloid_hits():
    metabolites_to_check = pd.read_csv(rubiaceae_apocynaceae_metabolites_output_csv).columns.tolist()

    alks_df = output_alkaloids_from_metabolites(metabolites_to_check, _rubiaceae_apocynaceae_alks_output_csv)

    rubs_apoc_metas_data = pd.read_csv(rubiaceae_apocynaceae_metabolites_output_csv)
    get_alkaloid_hits_for_taxa(rubs_apoc_metas_data, alks_df, rub_apoc_alkaloid_hits_output_csv,
                               fams=['Rubiaceae', 'Apocynaceae'])

def summarise_metabolites():
    metas_data = pd.read_csv(rubiaceae_apocynaceae_metabolites_output_csv)
    summ = metas_data.describe()
    print(summ)
    worthwhile_metabolites = [x for x in summ.columns if summ[x]['mean'] > 0.001]
    print(worthwhile_metabolites)


def get_rub_apoc_antibac_metabolite_hits():
    all_metas_data = pd.read_csv(rubiaceae_apocynaceae_metabolites_output_csv)
    get_antibac_metabolite_hits_for_taxa(all_metas_data, rub_apoc_antibac_metabolites_output_csv,
                                         fams=['Rubiaceae', 'Apocynaceae'])


def main():
    get_rub_apoc_metabolites()
    # recheck_taxa(_check_output_csv)
    summarise_metabolites()
    get_rub_apoc_antibac_metabolite_hits()
    get_rub_apoc_alkaloid_hits()


if __name__ == '__main__':
    main()