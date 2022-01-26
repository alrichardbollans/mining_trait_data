from typing import List

import numpy as np
import pandas as pd
import pykew.powo as powo
from pykew import powo_terms

from name_matching_cleaning import COL_NAMES, clean_urn_ids, get_accepted_name_info_from_IDS


def search_powo(search_terms: List[str], temp_output_file: str, accepted_output_file: str, filters: List[str] = None,
                characteristics_to_search: List[str] = None, families_of_interest: List[str] = None):
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
    :param search_terms:
    :param temp_output_file:
    :param accepted_output_file:
    :param filters:
    :param characteristics_to_search:
    :param families_of_interest:
    :return:
    """

    if characteristics_to_search is None:
        powocharacteristics_to_search = [powo_terms.Characteristic.characteristic, powo_terms.Characteristic.use,
                                         powo_terms.Characteristic.summary,
                                         powo_terms.Characteristic.leaf]
    else:
        powocharacteristics_to_search = [getattr(powo_terms.Characteristic, x) for x in characteristics_to_search]

    if filters is None:
        powofilters = None
    else:
        powofilters = [getattr(powo_terms.Filters, x) for x in filters]
    all_results = []

    for st in search_terms:
        for charac in powocharacteristics_to_search:
            if families_of_interest is not None:
                for fam in families_of_interest:
                    query = {charac: st, powo_terms.Name.family: fam}
                    all_results += powo.search_all_pages(query, filters=powofilters)
            else:
                query = {charac: st}

                all_results += powo.search_all_pages(query, filters=powofilters)

    list_of_all_individual_results = []
    for rs in all_results:
        try:
            list_of_all_individual_results += rs._response['results']
        except KeyError:
            pass
    df = pd.DataFrame(list_of_all_individual_results)
    df.rename(
        columns={'snippet': 'powo_Snippet',
                 'url': COL_NAMES['single_source'], 'family': 'Family'},
        inplace=True)
    if len(df.index) > 0:
        df['Source'] = 'POWO pages(' + df['Source'].astype(str) + ')'
        df['fqId'] = df['fqId'].apply(clean_urn_ids)
    else:
        df['Source'] = np.nan

    df.to_csv(temp_output_file)
    get_accepted_name_info_from_IDS('fqId', temp_output_file, accepted_output_file)


if __name__ == '__main__':
    search_powo(['spine', 'thorn', 'spike'], 'test.csv', 'acc_test.csv')
    # search_powo(['hairy'], 'test.csv', 'acc_test.csv', families_of_interest=['Rubiaceae', 'Apocynaceae'])
