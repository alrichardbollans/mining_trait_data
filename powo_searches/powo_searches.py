import os
from typing import List, Tuple

import numpy as np
import pandas as pd

from data_compilation_methods import single_source_col


def search_powo(search_terms: List[str], accepted_output_file: str, filters: List[str] = None,
                characteristics_to_search: List[str] = None, families_of_interest: List[str] = None, wcvp_version: str = None):
    """
    Possible characteristics
    summary
    use
    leaf

    characteristic
    appearance
    flower
    fruit
    inflorescence
    seed
    cloning

    Note: characteristic captures: seed, inflorescence, fruit, flower, cloning and appearance
    To find all possible hits set characteristics_to_search = [powo_terms.Characteristic.characteristic,
                                        powo_terms.Characteristic.use,
                                        powo_terms.Characteristic.summary,
                                        powo_terms.Characteristic.leaf] which is default
    Note since POWO update, the 'General' caterogy needs updating in pykew but I don't think this has been done.
    :param search_terms:
    :param temp_output_file:
    :param accepted_output_file:
    :param filters:
    :param characteristics_to_search:
    :param families_of_interest:
    :return:

    """
    from wcvpy.wcvp_download import get_all_taxa, wcvp_accepted_columns
    from wcvpy.wcvp_name_matching import clean_urn_ids, get_accepted_wcvp_info_from_ipni_ids_in_column
    import pykew.powo as powo
    from pykew import powo_terms
    import time

    if accepted_output_file is not None:
        out_dir = os.path.dirname(accepted_output_file)
        if not os.path.isdir(out_dir):
            if out_dir != '':
                os.mkdir(os.path.dirname(accepted_output_file))

    if characteristics_to_search is None:
        powocharacteristics_to_search = [powo_terms.Characteristic.characteristic,
                                         powo_terms.Characteristic.use,
                                         powo_terms.Characteristic.summary,
                                         powo_terms.Characteristic.leaf]
    else:
        powocharacteristics_to_search = [getattr(powo_terms.Characteristic, x) for x in
                                         characteristics_to_search]

    if filters is None:
        powofilters = None
    else:
        powofilters = [getattr(powo_terms.Filters, x) for x in filters]
    all_results = []

    for st in search_terms:
        time.sleep(1)
        for charac in powocharacteristics_to_search:
            time.sleep(1)
            if families_of_interest is not None:
                for fam in families_of_interest:
                    query = {charac: st, powo_terms.Name.family: fam}
                    results = powo.search(query, filters=powofilters)
                    try:
                        # If results has multiple pages
                        for r in results:
                            try:
                                all_results.append(r)
                            except KeyError:
                                pass
                    except AttributeError:
                        try:
                            for result in results._response['results']:
                                all_results.append(result)
                        except KeyError:
                            pass

            else:
                query = {charac: st}

                results = powo.search(query, filters=powofilters)
                try:
                    # If results has multiple pages
                    for r in results:
                        try:
                            all_results.append(r)
                        except KeyError:
                            pass
                except AttributeError:
                    try:
                        for result in results._response['results']:
                            all_results.append(result)
                    except KeyError:
                        pass
    df = pd.DataFrame(all_results)
    df.rename(
        columns={'snippet': 'powo_Snippet',
                 'url': single_source_col, 'family': 'Family'},
        inplace=True)
    if len(df.index) > 0:
        df[single_source_col] = 'POWO pages(' + df[single_source_col].astype(str) + ')'
        df['fqId'] = df['fqId'].apply(clean_urn_ids)
    else:
        df[single_source_col] = np.nan
    all_taxa = get_all_taxa(version=wcvp_version)
    acc_df = get_accepted_wcvp_info_from_ipni_ids_in_column(df, 'fqId', all_taxa)
    acc_df.sort_values(by=wcvp_accepted_columns['name']).to_csv(accepted_output_file)


def create_presence_absence_data(powo_hits: pd.DataFrame, terms_indicating_absence: List[str] = None,
                                 accepted_ipni_ids_of_absence: List[str] = None) -> Tuple[pd.DataFrame]:
    from wcvpy.wcvp_download import wcvp_accepted_columns
    if terms_indicating_absence is not None:
        absence_data = powo_hits[powo_hits['powo_Snippet'].str.contain('|'.join(terms_indicating_absence))]
        presence_data = powo_hits[~powo_hits['powo_Snippet'].str.contain('|'.join(terms_indicating_absence))]

    if accepted_ipni_ids_of_absence is not None:
        absence_data = powo_hits[powo_hits[wcvp_accepted_columns['ipni_id']].isin(accepted_ipni_ids_of_absence)]
        presence_data = powo_hits[~powo_hits[wcvp_accepted_columns['ipni_id']].isin(accepted_ipni_ids_of_absence)]

    if len(absence_data.index) + len(presence_data.index) != len(powo_hits.index):
        raise ValueError('Some values have been lost')

    return presence_data, absence_data
