import json
import os
import time
import uuid
from typing import List

import numpy as np
import pandas as pd
import requests

_classyfire_url = "http://classyfire.wishartlab.com"
_chunk_size = 100  # Unsure how to access all pages, so limit to number of results per page
_post_sleep_interval = float(60 / 12)  # Post requests should be limited to 12 per minute
_get_sleep_interval = 60


def get_classyfire_queries_from_smiles(smiles: List[str]):
    # API: https://bitbucket.org/wishartlab/classyfire_api/src/master/
    time.sleep(_post_sleep_interval)
    list_string = '\\n'.join(smiles)

    r = requests.post(_classyfire_url + '/queries.json', data='{"label": "%s", '
                                                              '"query_input": "%s", "query_type": "STRUCTURE"}'
                                                              % ('pyclassfyfire', list_string),
                      headers={"Content-Type": "application/json"})
    r.raise_for_status()
    return r.json()['id']


def get_classyfire_classes_from_query(query_id):
    r = requests.get('%s/queries/%s.%s' % (_classyfire_url, query_id, 'json'),
                     headers={"Content-Type": "application/%s" % 'json'})
    r.raise_for_status()
    result = json.loads(r.text)
    return result


def get_classyfire_classes_from_smiles(smiles: List[str], tempout_dir: str = None):
    unique_smiles = list(set(smiles))

    # First save time by reading previous temp outputs
    existing_df = None
    if tempout_dir is not None:
        existing_info = []
        for temp_cl_file in os.listdir(tempout_dir):
            if temp_cl_file.startswith('classyfireinfo_'):
                existing_info.append(pd.read_csv(os.path.join(tempout_dir, temp_cl_file), index_col=0))
        if len(existing_info) > 0:
            existing_df = pd.concat(existing_info)

            already_known_smiles = existing_df['original_SMILES'].tolist()
            # remove the item for all its occurrences
            for alread_known in already_known_smiles:
                c = unique_smiles.count(alread_known)
                for i in range(c):
                    unique_smiles.remove(alread_known)

    fields_to_collect = ['kingdom', 'superclass', 'class', 'subclass', 'direct_parent']
    out_df = pd.DataFrame()
    query_ids = []
    comps = []
    print('Getting query ids')
    for sm in unique_smiles:
        comps.append(sm)
        if not len(comps) % _chunk_size:
            query_ids.append(get_classyfire_queries_from_smiles(comps))
            comps = []
    if len(comps) > 0:
        query_ids.append(get_classyfire_queries_from_smiles(comps))
    query_count = 0
    while query_count < len(query_ids):
        print(f'Getting classes for {query_count + 1} out of {len(query_ids)} queries.')
        # need to work out how to preserve original smiles....
        query_id = query_ids[query_count]
        result = get_classyfire_classes_from_query(query_id)
        # Get info when query is done, if not wait.
        if result["classification_status"] == "Done":
            for inv_ent in result['invalid_entities']:
                original_position = unique_smiles.index(inv_ent['structure'])
                result['entities'].insert(original_position, {'identifier': None, 'smiles': inv_ent['structure']})
            for ent in result['entities']:
                ent_dict = {'classyfire_SMILES': ent['smiles']}
                if ent['identifier'] is not None:

                    for t in fields_to_collect:

                        if ent[t] is not None:
                            ent_dict['classyfire_' + t] = ent[t]['name']

                        else:
                            ent_dict['classyfire_' + t] = np.nan

                    i_nodes = []
                    for i_node in ent['intermediate_nodes']:
                        i_nodes.append(i_node['name'])
                    ent_dict['classyfire_intermediate_nodes'] = ':'.join(i_nodes)

                    alt_parents = []
                    for alt_p in ent['alternative_parents']:
                        alt_parents.append(alt_p['name'])
                    ent_dict['classyfire_alternative_parents'] = str(alt_parents)

                    ent_dict['substituents'] = str(ent['substituents'])

                ent_df = pd.DataFrame(ent_dict, index=[result['entities'].index(ent) + (query_count * _chunk_size)])
                out_df = pd.concat([out_df, ent_df])

            query_count += 1
        else:
            print(f'Waiting. {query_count} out of {len(query_ids)} queries complete')
            time.sleep(_get_sleep_interval)
    if len(out_df.index) > 0:
        out_df['original_SMILES'] = unique_smiles
        out_df = out_df[['original_SMILES', 'classyfire_SMILES'] + [c for c in out_df.columns if c not in ['original_SMILES', 'classyfire_SMILES']]]

    if tempout_dir is not None:
        if len(out_df.index) > 0:
            out_df.to_csv(os.path.join(tempout_dir, 'classyfireinfo_' + str(uuid.uuid4()) + '.csv'))
        if existing_df is not None:
            out_df = pd.concat([out_df, existing_df])

    out_df = out_df.sort_values(by='original_SMILES')
    out_df = out_df.reset_index(drop=True)
    return out_df


def get_classyfire_classes_from_df(df: pd.DataFrame, smiles_col: str, tempout_dir: str = None) -> pd.DataFrame:
    classyfire_info = get_classyfire_classes_from_smiles(df[smiles_col].dropna(), tempout_dir)
    classyfire_info = classyfire_info.rename(columns={'original_SMILES': 'SMILES'})
    all_metabolites_with_class_info = pd.merge(df, classyfire_info, how='left', on='SMILES')

    return all_metabolites_with_class_info
