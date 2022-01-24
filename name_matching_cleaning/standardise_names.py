import os
import subprocess

import pandas as pd

path_here = os.path.dirname(os.path.abspath(__file__))

# TODO: Resolve all instances of multiple matches
# TODO: Create batching
def standardise_names_in_column(column_to_standardise: str, input_file: str, output_file: str):
    if " " in column_to_standardise:
        print('This will likely raise an error. R imports spaces as ".". Suggest changing spaces to full stops.')
    print(path_here)
    print(input_file)
    r_script = os.path.join(path_here, 'standardise_names.R')
    command = f'Rscript "{r_script}" --input "{input_file}" --out "{output_file}" --colname "{column_to_standardise}" --packagepath "{path_here}"'

    subprocess.call(command, shell=True)


def batch_standardise_names(column_to_standardise: str, input_file: str, output_file=None):
    too_large = pd.read_csv(input_file)
    print(too_large)
    matching_data_dir = os.path.join(path_here, 'matching data', 'batches')
    batches = [too_large.loc[1000 * i:1000 * i + 999] for i in range(0, (len(too_large.index) // 1000) + 1)]
    # TODO: Needs finishing

    for i in range(0, len(batches)):
        print(i)
        filename = str(i) + ".csv"
        batch_file = os.path.join(matching_data_dir, filename)
        batch = batches[i]
        batch.to_csv(batch_file)
        print(batch)
        standardise_names_in_column(column_to_standardise, batch_file, batch_file)


def get_accepted_name_info_from_IDS(column_to_standardise: str, input_file: str, output_file: str):
    print(path_here)
    print(input_file)
    r_script = os.path.join(path_here, 'standardise_ids.R')
    command = f'Rscript "{r_script}" --input "{input_file}" --out "{output_file}" --colname "{column_to_standardise}"'

    subprocess.call(command, shell=True)
