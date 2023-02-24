import ast
import os
from typing import List

import pandas as pd

from data_compilation_methods import COL_NAMES


def output_summary_of_hit_csv(input_csv: str, output_csv_stub: str, families: List[str] = None,
                              ranks: List[str] = None,
                              source_translations: dict = None, check_duplicates=True):
    if not os.path.isdir(os.path.dirname(output_csv_stub)):
        os.mkdir(os.path.dirname(output_csv_stub))

    from matplotlib import pyplot as plt
    out_df = pd.read_csv(input_csv)

    dup_hits_df = out_df[out_df.duplicated(subset=COL_NAMES['acc_id'])]
    if len(dup_hits_df) > 0:
        print(f'Duplicate hits found')
        if check_duplicates:
            raise ValueError

    out_df.drop_duplicates(subset=[COL_NAMES['acc_id']], inplace=True)

    if ranks is not None:
        out_df = out_df[out_df[COL_NAMES['acc_rank']].isin(ranks)]

    if families is not None:
        out_df = out_df[out_df[COL_NAMES['acc_family']].isin(families)]

    source_counts = dict()
    source_unique_counts = dict()

    source_counts['Total'] = len(out_df['Compiled_Sources'].values)
    total = len(out_df['Compiled_Sources'].values)
    source_unique_counts['Total'] = total

    for sources_str in out_df['Compiled_Sources'].values:

        split_sources = ast.literal_eval(sources_str)

        for s in split_sources:
            if s not in source_counts.keys():
                source_counts[s] = 1
            else:
                source_counts[s] += 1

        if len(split_sources) == 1:
            s = split_sources[0]
            if s not in source_unique_counts.keys():
                source_unique_counts[s] = 1
            else:
                source_unique_counts[s] += 1

    # Compress sources
    if source_translations is not None:
        for key in source_translations.keys():
            source_counts[key] = 0
            source_unique_counts[key] = 0

        keys_to_remove = []
        for key in source_counts.keys():
            for source in source_translations.keys():
                if source_translations[source] in key:
                    source_counts[source] += (source_counts[key])
                    if key not in keys_to_remove:
                        keys_to_remove.append(key)

        for key in source_unique_counts.keys():
            for source in source_translations.keys():
                if source_translations[source] in key:
                    source_unique_counts[source] += (source_unique_counts[key])
                    if key not in keys_to_remove:
                        keys_to_remove.append(key)

        for k in keys_to_remove:
            if k in source_counts.keys():
                del source_counts[k]
            if k in source_unique_counts.keys():
                del source_unique_counts[k]

    new_keys_to_remove = []
    for k in source_counts:
        if source_counts[k] == 0:
            new_keys_to_remove.append(k)
    for k in new_keys_to_remove:
        del source_counts[k]

    new_keys_to_remove = []
    for k in source_unique_counts:
        if source_unique_counts[k] == 0:
            new_keys_to_remove.append(k)
    for k in new_keys_to_remove:
        del source_unique_counts[k]

    source_count_df = pd.DataFrame.from_dict(source_counts, orient='index', columns=['Count'])
    source_unique_counts_df = pd.DataFrame.from_dict(source_unique_counts, orient='index', columns=['Count'])

    source_count_df.to_csv(output_csv_stub + '.csv')
    source_unique_counts_df.to_csv(output_csv_stub + '_unique.csv')

    plot_threshold = 0
    plt.bar(source_count_df[source_count_df['Count'] > plot_threshold].index,
            source_count_df[source_count_df['Count'] > plot_threshold]['Count'].values.tolist(),
            edgecolor='black')
    plt.xticks(rotation=65)
    plt.xlabel('Source')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(output_csv_stub + '.png')
    plt.close()

    # plt.bar(source_count_df.index, source_count_df['Count'].values.tolist(), edgecolor='black')
    # plt.xticks(rotation=65)
    # plt.xlabel('Source')
    # plt.ylabel('Count')
    # plt.tight_layout()
    # plt.savefig(output_csv_stub + '.png')
    # plt.close()

    # plt.bar(source_unique_counts_df.index, source_unique_counts_df['Count'].values.tolist(), edgecolor='black')
    # plt.xticks(rotation=65)
    # plt.xlabel('Unique Source')
    # plt.ylabel('Count')
    # plt.tight_layout()
    # plt.savefig(output_csv_stub + '_unique.png')
    # plt.close()

    plt.bar(source_unique_counts_df[source_unique_counts_df['Count'] > plot_threshold].index,
            source_unique_counts_df[source_unique_counts_df['Count'] > plot_threshold][
                'Count'].values.tolist(),
            edgecolor='black')
    plt.xticks(rotation=65)
    plt.xlabel('Unique Source')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(output_csv_stub + '_unique.png')
    plt.close()

    return source_counts, source_unique_counts


def _main():
    ### Examples
    from pkg_resources import resource_filename

    _inputs_path = os.path.join(resource_filename(__name__, 'unittests'), 'test_inputs')
    _outputs_path = os.path.join(resource_filename(__name__, 'unittests'), 'test_outputs')
    test_df = pd.read_csv(os.path.join(_inputs_path, 'list_of_poisonous_plants.csv'))
    # filter_df_by_families(test_df, ['Apocynaceae'])

    summary_stub = os.path.join(_outputs_path, 'source_summary')
    source_counts, source_uniq_counts = output_summary_of_hit_csv(
        os.path.join(_inputs_path, 'list_of_poisonous_plants.csv'),
        summary_stub, families=['Apocynaceae', 'Rubiaceae', 'Loganiaceae'],
        source_translations={'Wiki': '_wiki', 'POWO': 'POWO pages'})
    # pass


if __name__ == '__main__':
    _main()
