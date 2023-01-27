import os.path

import pandas as pd
from pkg_resources import resource_filename

from knapsack_searches import kn_metabolite_name_column

_inputs_path = resource_filename(__name__, 'inputs')


def alkaloid_class_from_metabolite(metabolite: str, translation_dict: dict):
    out_tuple = []
    for alk_class in translation_dict:
        if metabolite in translation_dict[alk_class]:
            out_tuple.append(alk_class)

    return tuple(out_tuple)


def get_class_information_dict() -> dict:
    def _unique_tuple(iterable):
        return tuple(set(sorted(iterable)))

    manual_class_information = pd.read_csv(
        os.path.join(_inputs_path, 'manual_Alkaloid_Class_Classification.csv'))

    grouped = manual_class_information.groupby('Class')['Alkaloids'].apply(
        _unique_tuple).reset_index(
        name='grouped_Alkaloids')
    df = pd.merge(manual_class_information, grouped, how='left',
                  on='Class')

    return pd.Series(df['grouped_Alkaloids'].values,
                     index=df['Class']).to_dict()


def get_alkaloid_classes_from_metabolites(metabolites_table: pd.DataFrame,
                                          output_csv: str = None) -> pd.DataFrame:
    '''

    :param metabolites_table: from get_metabolites_in_family
    :param temp_output_csv:
    :param output_csv:
    :return:
    '''

    class_t_dict = get_class_information_dict()
    df_copy = metabolites_table.copy(deep=True)
    df_copy['alkaloid_class'] = df_copy[kn_metabolite_name_column].apply(
        lambda x: alkaloid_class_from_metabolite(x, class_t_dict))

    if output_csv is not None:
        df_copy.to_csv(output_csv)

    return df_copy
