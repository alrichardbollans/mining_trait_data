import hashlib
import json
import os

import numpy as np
import pandas as pd
import requests
from typing import List

from pkg_resources import resource_filename

inputs_path = resource_filename(__name__, 'inputs')
temp_outputs_dir = 'name matching temp outputs'


def get_knms_name_matches(names: List[str]):
    """
    Searches knms for matching names
    :param names:
    :return:
    """
    # Save previous searches using a hash of names to avoid repeating searches
    names = list(names)
    unique_name_list = []
    for x in names:
        if x not in unique_name_list:
            unique_name_list.append(x)

    str_to_hash = str(unique_name_list).encode()
    temp_csv = "knmns_matches_" + str(hashlib.md5(str_to_hash).hexdigest()) + ".csv"

    try:
        os.mkdir(temp_outputs_dir)
    except FileExistsError as error:
        pass

    temp_output_knms_csv = os.path.join(temp_outputs_dir, temp_csv)
    if os.path.isfile(temp_output_knms_csv):
        # Pandas will read TRUE/true as bools and therefore as True rather than true
        records = pd.read_csv(temp_output_knms_csv, dtype={'match_state': str}, index_col=0)
    else:
        knms_url = "http://namematch.science.kew.org/api/v2/powo/match"
        res = requests.post(knms_url, json=unique_name_list)
        headings = ['submitted', 'match_state', 'ipni_id', 'matched_name']

        content = json.loads(res.content.decode('utf-8'))
        try:
            if all(len(content["records"][x]) == 2 for x in range(len(content["records"]))):
                shortened_headings = ['submitted', 'match_state']
                records = pd.DataFrame(content["records"], columns=shortened_headings)
                records['ipni_id'] = np.nan
                records['matched_name'] = np.nan
            else:
                records = pd.DataFrame(content["records"], columns=headings)
        except ValueError:
            raise requests.ConnectionError('records not retrievd due to server error')
        records.replace('', np.nan, inplace=True)
        records['submitted'].ffill(inplace=True)
        records['match_state'].ffill(inplace=True)

        records.to_csv(temp_output_knms_csv)

    return records
