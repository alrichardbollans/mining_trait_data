import os

import pandas as pd
from pkg_resources import resource_filename

import wikipedia_searches
### Inputs


inputs_path = resource_filename(__name__, '../inputs')
species_csv = os.path.join(inputs_path, 'standardised_order.csv')

### Outputs
output_path = resource_filename(__name__, 'outputs')
output_wiki_csv = os.path.join(output_path, 'list_plants_with_wiki_pages.csv')

def main():
    species_data = pd.read_csv(species_csv)
    species_data.set_index('Accepted_Name', inplace=True)

    species_list = species_data.index

    wikipedia_searches.make_wiki_hit_df(species_list, output_wiki_csv)



if __name__ == '__main__':
    main()
