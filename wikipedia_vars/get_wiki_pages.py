import os

import pandas as pd
from pkg_resources import resource_filename

import wikipedia_searches
### Inputs
from taxa_lists.get_taxa_from_wcvp import get_accepted_taxa

### Outputs
output_path = resource_filename(__name__, 'outputs')
output_wiki_csv = os.path.join(output_path, 'list_plants_with_wiki_pages.csv')

def main():
    accepted_data = get_accepted_taxa(families_of_interest=['Apocynaceae', 'Rubiaceae'])

    ranks_to_use = ["SPECIES", "VARIETY", "SUBSPECIES"]

    accepted_taxa = accepted_data.loc[accepted_data["rank"].isin(ranks_to_use)]

    species_list = accepted_taxa["taxon_name"].values

    wikipedia_searches.make_wiki_hit_df(species_list, output_wiki_csv)



if __name__ == '__main__':
    main()
