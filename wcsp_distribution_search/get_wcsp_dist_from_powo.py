from typing import List

import pandas as pd

from automatchnames import get_accepted_info_from_ids_in_column
from tqdm import tqdm


def search_powo_for_tdwg3_distributions(ipni_list: List[str], out_pkl: str):
    import pykew.powo as powo
    from json import JSONDecodeError
    import time
    import pickle

    # Note distributions aren't given for synonyms, so this function looks up the accepted taxa in these cases.

    out = {}
    for i in tqdm(range(len(ipni_list)), desc="Searching POWO for dists…", ascii=False, ncols=72):

        time.sleep(1)
        ipni = ipni_list[i]
        lookup_str = 'urn:lsid:ipni.org:names:' + str(ipni)
        try:

            res = powo.lookup(lookup_str, include=['distribution'])
            try:
                if res['synonym']:
                    fq_id = res['accepted']['fqId']

                    res = powo.lookup(fq_id, include=['distribution'])
            except KeyError:
                pass

            native_codes = []
            introduced_codes = []
            extinct_codes = []
            try:
                native_to = [d['tdwgCode'] for d in res['distribution']['natives'] if d['tdwgLevel'] == 3]
                native_codes += native_to

            except KeyError:
                pass

            finally:
                try:
                    introduced_to = [d['tdwgCode'] for d in res['distribution']['introduced'] if d['tdwgLevel'] == 3]
                    introduced_codes += introduced_to

                except KeyError:

                    pass

                finally:
                    try:
                        extinct_to = [d['tdwgCode'] for d in res['distribution']['extinct'] if d['tdwgLevel'] == 3]
                        extinct_codes += extinct_to

                    except KeyError:

                        pass

                    finally:
                        if (len(native_codes) + len(introduced_codes) + len(extinct_codes)) == 0:
                            print(f'No dist codes for {ipni}')
                    out[ipni] = [native_codes, introduced_codes, extinct_codes]
                with open(out_pkl, 'wb') as f:
                    pickle.dump(out, f)
        except JSONDecodeError:
            print(f'json error: {ipni}')


def convert_pkl_to_df(in_pkl: str, out_csv: str):
    import pickle
    with open(in_pkl, 'rb') as f:
        dist_dict = pickle.load(f)

    native_dict = {}
    intro_dict = {}
    ext_dict = {}
    for k in dist_dict.keys():
        native_dict[k] = str(dist_dict[k][0])
        intro_dict[k] = str(dist_dict[k][1])
        ext_dict[k] = str(dist_dict[k][2])
    value_dict = {'kew_id': list(dist_dict.keys()),
                  'native_tdwg3_codes': list(native_dict.values()),
                  'intro_tdwg3_codes': list(intro_dict.values()),
                  'extinct_tdwg3_codes': list(ext_dict.values())}
    out_df = pd.DataFrame(value_dict)
    acc_out_df = get_accepted_info_from_ids_in_column(out_df, 'kew_id')
    acc_out_df.to_csv(out_csv)
