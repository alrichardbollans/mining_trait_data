import os

from pkg_resources import resource_filename

import wikipedia_searches
### Inputs
from taxa_lists.get_taxa_from_wcvp import get_all_taxa

### Outputs
_output_path = resource_filename(__name__, 'outputs')
output_wiki_csv = os.path.join(_output_path, 'list_plants_with_wiki_pages.csv')
more_checked_taxa_csv = os.path.join(_output_path, 'initially_missed_taxa.csv')


def main():
    data = get_all_taxa(families_of_interest=['Apocynaceae', 'Rubiaceae'], accepted=True)

    ranks_to_use = ["Species", "Variety", "Subspecies"]

    taxa = data.loc[data["rank"].isin(ranks_to_use)]

    species_list = taxa["taxon_name"].values

    wikipedia_searches.make_wiki_hit_df(species_list, output_wiki_csv)


if __name__ == '__main__':
    main()
    # wikipedia_searches.make_wiki_hit_df(['Hoya crassipetiolata','Hoya crassipetiolata'], more_checked_taxa_csv)
