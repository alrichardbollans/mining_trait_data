import os.path

import pandas as pd
from pkg_resources import resource_filename

from knapsack_searches import kn_metabolite_name_column

_inputs_path = resource_filename(__name__, 'inputs')
alkaloid_class_output_column = 'alkaloid_classes'


def alkaloid_class_from_metabolite(metabolite: str):
    class_t_dict = get_class_information_dict()

    return class_t_dict[clean_metabolite_col(metabolite)]


def clean_metabolite_col(given_str: str):
    out_str = given_str.lower()
    out_str = out_str.strip()
    out_str = out_str.replace('(-)-', '')
    out_str = out_str.replace('(+)-', '')
    out_str = out_str.replace('(+/-)-', '')
    return out_str


def get_class_information_dict() -> dict:
    def _unique_join(iterable):
        return ';'.join(set(sorted(iterable)))

    manual_class_information = pd.read_excel(
        os.path.join(_inputs_path, 'Metabolite Alkaloid Class Classification.xlsx'), sheet_name='Metabolites')

    duplicates = manual_class_information[manual_class_information['Alkaloids'].duplicated(keep=False)]
    if len(duplicates.index) > 0:
        print(duplicates)
        raise ValueError(
            f'Repeated alkaloid class entries in file {os.path.join(_inputs_path, "Metabolite Alkaloid Class Classification.xlsx")}')

    # clean
    manual_class_information['Alkaloids'] = manual_class_information['Alkaloids'].apply(
        clean_metabolite_col)
    manual_class_information['Class'] = manual_class_information['Class'].apply(
        clean_metabolite_col)

    grouped = manual_class_information.groupby('Alkaloids')['Class'].apply(
        _unique_join).reset_index(
        name='grouped_classes')

    return pd.Series(grouped['grouped_classes'].values,
                     index=grouped['Alkaloids']).to_dict()


def get_alkaloid_classes_from_metabolites(metabolites_table: pd.DataFrame,
                                          metabolite_name_col: str = None,
                                          output_csv: str = None) -> pd.DataFrame:
    '''

    :param metabolites_table: from get_metabolites_in_family
    :param temp_output_csv:
    :param output_csv:
    :return:
    '''

    class_t_dict = get_class_information_dict()
    df_copy = metabolites_table.copy(deep=True)

    if metabolite_name_col is None:
        metabolite_name_col = kn_metabolite_name_column
    df_copy['cleaned_metabolite_col'] = df_copy[metabolite_name_col].apply(clean_metabolite_col)
    df_copy[alkaloid_class_output_column] = df_copy['cleaned_metabolite_col'].apply(
        lambda x: class_t_dict[x] if x in class_t_dict.keys() else '')

    if output_csv is not None:
        df_copy.to_csv(output_csv)

    return df_copy

if __name__ == '__main__':
    manual_class_information = pd.read_excel(
        os.path.join(_inputs_path, 'Metabolite Alkaloid Class Classification.xlsx'), sheet_name='Metabolites')
    print([x.lower() for x in manual_class_information['Class'].unique()])
