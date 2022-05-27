import numpy as np

import requests
from pygbif import occurrences as occ



def get_elevation_from_gbif_key(gbifkey: int):
    gbifkey = int(gbifkey)

    # Note package issue https://github.com/gbif/pygbif/issues/93
    try:
        record = occ.get(key=gbifkey)

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:

            return np.nan
        else:
            print(e)
            print(gbifkey)
            return 'retry'

    try:
        return record['elevation']
    except KeyError:
        return np.nan
