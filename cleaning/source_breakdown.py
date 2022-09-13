import ast
import os

import pandas as pd
from automatchnames import COL_NAMES


def output_summary_of_hit_csv(input_csv: str, output_csv_stub: str, plot_threshold=100,
                              plot_unique_threshold=50, check_duplicates=True):
    from matplotlib import pyplot as plt
    out_df = pd.read_csv(input_csv)

    dup_hits_df = out_df[out_df.duplicated(subset=COL_NAMES['acc_id'])]
    if len(dup_hits_df) > 0:
        print(f'Duplicate hits found')
        if check_duplicates:
            raise ValueError

    out_df.drop_duplicates(subset=['Accepted_ID'], inplace=True)
    source_translations = {'Wiki': '_wiki', 'POWO': 'POWO pages'}
    source_counts = dict()
    source_unique_counts = dict()

    source_counts['Total'] = len(out_df['Compiled_Sources'].values)
    source_unique_counts['Total'] = len(out_df['Compiled_Sources'].values)
    for sources_str in out_df['Compiled_Sources'].values:

        split_sources = ast.literal_eval(sources_str)
        # split_sources = [x for x in split_sources if x != '']

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

    source_counts['POWO'] = 0
    source_unique_counts['POWO'] = 0
    source_counts['Wiki'] = 0
    source_unique_counts['Wiki'] = 0

    for key in source_counts.keys():
        for source in source_translations.keys():
            if source_translations[source] in key:
                source_counts[source] += (source_counts[key])

    for key in source_unique_counts.keys():
        for source in source_translations.keys():
            if source_translations[source] in key:
                source_unique_counts[source] += (source_unique_counts[key])

    source_count_df = pd.DataFrame.from_dict(source_counts, orient='index', columns=['Count'])
    source_unique_counts_df = pd.DataFrame.from_dict(source_unique_counts, orient='index', columns=['Count'])

    source_count_df.to_csv(output_csv_stub + '.csv')
    source_unique_counts_df.to_csv(output_csv_stub + '_unique.csv')

    plt.bar(source_count_df[source_count_df['Count'] > plot_threshold].index,
            source_count_df[source_count_df['Count'] > plot_threshold]['Count'].values.tolist(), edgecolor='black')
    plt.xticks(rotation=65)
    plt.xlabel('Source')
    plt.ylabel('Count')
    plt.tight_layout()
    # plt.show()
    plt.savefig(output_csv_stub + '_example.png')
    plt.close()

    plt.bar(source_count_df.index, source_count_df['Count'].values.tolist(), edgecolor='black')
    plt.xticks(rotation=65)
    plt.xlabel('Source')
    plt.ylabel('Count')
    plt.tight_layout()
    # plt.show()
    plt.savefig(output_csv_stub + '.png')
    plt.close()

    plt.bar(source_unique_counts_df.index, source_unique_counts_df['Count'].values.tolist(), edgecolor='black')
    plt.xticks(rotation=65)
    plt.xlabel('Source')
    plt.ylabel('Count')
    plt.tight_layout()
    # plt.show()
    plt.savefig(output_csv_stub + '_unique.png')
    plt.close()

    plt.bar(source_unique_counts_df[source_unique_counts_df['Count'] > plot_unique_threshold].index,
            source_unique_counts_df[source_unique_counts_df['Count'] > plot_unique_threshold]['Count'].values.tolist(),
            edgecolor='black')
    plt.xticks(rotation=65)
    plt.xlabel('Source')
    plt.ylabel('Count')
    plt.tight_layout()
    # plt.show()
    plt.savefig(output_csv_stub + '_unique_example.png')
    plt.close()

    return source_counts, source_unique_counts


def _main():
    ### Examples
    from pkg_resources import resource_filename

    _inputs_path = os.path.join(resource_filename(__name__, 'unittests'), 'test_inputs')
    _outputs_path = os.path.join(resource_filename(__name__, 'unittests'), 'test_outputs')
    summary_stub = os.path.join(_outputs_path, 'source_summary')
    source_counts, source_uniq_counts = output_summary_of_hit_csv(
        os.path.join(_inputs_path, 'list_of_poisonous_plants.csv'),
        summary_stub)
    pass


if __name__ == '__main__':
    _main()
