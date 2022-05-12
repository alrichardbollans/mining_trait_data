import pickle
import time
from json import JSONDecodeError
from typing import List

import pandas as pd
import pykew.powo as powo
from automatchnames import get_accepted_info_from_ids_in_column
from tqdm import tqdm


def search_powo_for_distributions(ipni_list: List[str], out_pkl: str):
    # Note distributions aren't given for synonyms. This is fine except in cases where you use an id which is
    # no longer accepted
    # Also, this function does not return distributions of extinct taxa

    out = {}
    for i in tqdm(range(len(ipni_list)), desc="Searching POWO for dists…", ascii=False, ncols=72):

        time.sleep(1)
        ipni = ipni_list[i]
        lookup_str = 'urn:lsid:ipni.org:names:' + str(ipni)
        try:

            res = powo.lookup(lookup_str, include=['distribution'])
            dist_codes = []
            try:
                native_to = [d['tdwgCode'] for d in res['distribution']['natives']]
                dist_codes += native_to
            except KeyError:
                print(f'No native codes: {ipni}')

            finally:
                try:
                    introduced_to = [d['tdwgCode'] for d in res['distribution']['introduced']]
                    dist_codes += introduced_to
                except KeyError:

                    pass

                finally:
                    out[ipni] = dist_codes
                with open(out_pkl, 'wb') as f:
                    pickle.dump(out, f)
        except JSONDecodeError:
            print(f'json error: {ipni}')


def convert_pkl_to_df(in_pkl: str, out_csv: str):
    with open(in_pkl, 'rb') as f:
        dist_dict = pickle.load(f)

    str_dict = {}
    for k in dist_dict.keys():
        str_dict[k] = str(dist_dict[k])
    value_dict = {'kew_id': list(str_dict.keys()), 'iso3_codes': list(str_dict.values())}
    out_df = pd.DataFrame(value_dict)
    acc_out_df = get_accepted_info_from_ids_in_column(out_df, 'kew_id')
    acc_out_df.to_csv(out_csv)
