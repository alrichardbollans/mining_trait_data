import os
import zipfile
import io
from urllib.parse import urlparse

import pandas as pd
import requests
from pkg_resources import resource_filename

inputs_path = resource_filename(__name__, 'inputs')

outputs_path = resource_filename(__name__, 'outputs')

# Standardise rank names
def capitalize_ranks(g: str):
    try:
        l = g.lower()
        return l.capitalize()
    except AttributeError:
        return g

def get_accepted_taxa(families_of_interest=None, output_csv=None, wcvp_input_file=None, wcvp_link=None):
    get_all_taxa(families_of_interest, output_csv, wcvp_input_file, wcvp_link, accepted=True)


def get_all_taxa(families_of_interest=None, output_csv=None, wcvp_input_file=None, wcvp_link=None,
                 accepted=False) -> pd.DataFrame:
    if wcvp_link is None:
        wcvp_link = 'http://sftp.kew.org/pub/data-repositories/WCVP/wcvp_v7_dec_2021.zip'
    if wcvp_input_file is None:
        wcvp_input_file = os.path.join(inputs_path, 'wcvp_v7_dec_2021.txt')

    # Download if doesn't exist
    if not os.path.exists(wcvp_input_file):
        r = requests.get(wcvp_link, stream=True)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(inputs_path)

        a = urlparse(wcvp_link)

        basename_from_url = os.path.basename(a.path).replace('.zip', '.txt')

        wcvp_input_file = os.path.join(inputs_path, basename_from_url)

    wcvp_data = pd.read_csv(wcvp_input_file, sep='|')
    if families_of_interest is not None:
        wcvp_data = wcvp_data.loc[wcvp_data['family'].isin(families_of_interest)]

    if accepted:
        wcvp_data = wcvp_data[wcvp_data['taxonomic_status'] == 'Accepted']

    wcvp_data['rank'] = wcvp_data['rank'].apply(capitalize_ranks)
    # Remove unplaced taxa
    wcvp_data = wcvp_data[wcvp_data['taxonomic_status'] != 'Unplaced']

    if output_csv is not None:
        wcvp_data.to_csv(output_csv)



    return wcvp_data


def main():
    get_all_taxa(output_csv=os.path.join(outputs_path, 'wcvp_all_taxa.csv'))
    # get_accepted_taxa(output_csv=os.path.join(outputs_path, 'wcvp_accepted_taxa.csv'))
    # get_accepted_taxa(families_of_interest=['Apocynaceae', 'Rubiaceae'],
    #                   output_csv=os.path.join(outputs_path, 'wcvp_accepted_taxa_apocynaceae_rubiaceae.csv'))


if __name__ == '__main__':
    main()
