import re

import numpy as np


def clean_ids(given_value: str) -> str:
    '''
    Strips urn:lsid:ipni.org:names: from id
    '''
    try:
        if re.search('urn:lsid:ipni.org:names:', given_value):
            pos = re.search('urn:lsid:ipni.org:names:', given_value).end()
            return given_value[pos:]
        else:
            return np.nan
    except TypeError:
        return given_value
