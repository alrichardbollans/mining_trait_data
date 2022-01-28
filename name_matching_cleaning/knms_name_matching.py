import hashlib
import json
import os

import numpy as np
import pandas as pd
import requests
from typing import List

from pkg_resources import resource_filename

inputs_path = resource_filename(__name__, 'inputs')
temp_outputs_name_matching = resource_filename(__name__, 'temp_outputs')

def get_knms_name_matches(names: List[str]):
    """
    Searches knms for matching names
    :param names:
    :return:
    """
    # Save previous searches using a hash of names to avoid repeating searches
    names = list(names)
    str_to_hash = str(names).encode()
    temp_csv = str(hashlib.md5(str_to_hash).hexdigest()) + ".csv"

    temp_output_knms_csv = os.path.join(temp_outputs_name_matching, temp_csv)
    if os.path.isfile(temp_output_knms_csv):
        # Pandas will read TRUE/true as bools and therefore as True rather than true
        records = pd.read_csv(temp_output_knms_csv, dtype={'match_state': str})
    else:
        knms_url = "http://namematch.science.kew.org/api/v2/powo/match"
        res = requests.post(knms_url, json=names)
        headings = ['submitted', 'match_state', 'ipni_id', 'matched_name']

        content = json.loads(res.content.decode('utf-8'))
        records = pd.DataFrame(content["records"], columns=headings)
        records.replace('', np.nan, inplace=True)
        records['submitted'].ffill(inplace=True)
        records['match_state'].ffill(inplace=True)

        records.to_csv(temp_output_knms_csv)

    return records


def clear_temp_files():
    """
    Deletes temporary files
    :return:
    """
    for f in os.listdir(temp_outputs_name_matching):
        os.remove(f)