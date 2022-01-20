import os

import pandas as pd
from pkg_resources import resource_filename

inputs_path = resource_filename(__name__, 'inputs')

outputs_path = resource_filename(__name__, 'outputs')


def load_wcvp(families_of_interest=None, output_csv=None) -> pd.DataFrame:
    # Manually downloaded from http://sftp.kew.org/pub/data-repositories/WCVP/
    wcvp_input_CSV = os.path.join(inputs_path, 'wcvp_v7_dec_2021.txt')
    wcvp_data = pd.read_csv(wcvp_input_CSV, sep='|')
    if families_of_interest is not None:
        wcvp_data = wcvp_data.loc[wcvp_data['family'].isin(families_of_interest)]

    wcvp_data = wcvp_data[wcvp_data['taxonomic_status'] == 'Accepted']

    if output_csv is None:
        wcvp_data.to_csv(os.path.join(outputs_path, 'wcvp_accepted_taxa.csv'))
    else:
        wcvp_data.to_csv(output_csv)

    return wcvp_data


def main():
    load_wcvp()


if __name__ == '__main__':
    main()
