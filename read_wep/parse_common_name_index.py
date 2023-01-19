import pandas as pd
# import parser object from tike
from tqdm import tqdm
from typing import List

from wcvp_download import get_all_taxa
from wcvp_name_matching import get_accepted_info_from_names_in_column

from read_wep import wiersema_input


def compress_lines_into_names(all_text_lines):
    """
    Takes list of lines in pdf and concatenate those lines which are names spread over multiple lines
    :param all_text_lines:
    :return:
    """
    new_lines = []
    iterable = iter(range(len(all_text_lines)))
    for i in iterable:
        line = all_text_lines[i]
        if line == '' or line == ' ':
            continue
        elif ' -' in line:
            new_line = line
            count = 0
            for l in range(i + 1, len(all_text_lines)):
                next_line = all_text_lines[l]
                if ' -' not in next_line:
                    new_line += next_line
                    count += 1
                else:
                    break
            new_lines.append(new_line)
            [next(iterable) for x in range(count)]
        else:
            new_lines.append(line)

    return new_lines


def common_names_from_index(output_csv: str = None):
    from bs4 import BeautifulSoup
    from tika import parser
    from io import StringIO

    # opening pdf file with xml content
    parsed_pdf = parser.from_file(wiersema_input, xmlContent=True)
    all_text = parsed_pdf['content']

    common_names = []
    scientific_names = []

    # Parse xml content to get distinct pages
    xhtml_data = BeautifulSoup(all_text, features="lxml")
    all_pages = xhtml_data.find_all('div', attrs={'class': 'page'})
    # right hand script common names appear on rhs of scientific names
    # This catches most of these cases, but it is not critical if we miss some
    right_handscripts_arab = range(1283, 1289)
    right_handscripts_hebrew = range(1309, 1313)
    for i in tqdm(
            range(775, len(all_pages)), desc="Searching pages", ascii=False,
            ncols=72):
        content = all_pages[i]
        _buffer = StringIO()
        _buffer.write(str(content))
        parsed_content = parser.from_buffer(_buffer.getvalue())

        # Get useful lines
        common_names_lines = compress_lines_into_names(parsed_content['content'].split('\n'))

        # Get common and scientific names from lines
        for line in common_names_lines:
            try:
                if i in right_handscripts_arab or i in right_handscripts_hebrew:
                    scientific_name = line[1:line.index(' -')]
                    common_name = line[line.index(' -') + 3:-1]
                else:
                    common_name = line[0:line.index(' -')]
                    scientific_name = line[line.index(' -') + 3:-1]
                common_names.append(common_name)
                scientific_names.append(scientific_name)
            except ValueError:
                # print(line)
                pass
    out_df = pd.DataFrame({'name': scientific_names, 'common_names': common_names})
    out_df['WEP_snippet'] = out_df.groupby(['name'])['common_names'].transform(lambda x: ':'.join(x))
    out_df.drop(columns=['common_names'], inplace=True)
    out_df.dropna(subset=['name'], inplace=True)
    out_df = out_df.drop_duplicates(subset=['name'])

    out_df['Source'] = 'WEP (Wiersema 2013)'
    acc_df = get_accepted_info_from_names_in_column(out_df, 'name')
    if output_csv is not None:
        acc_df.to_csv(output_csv)
    return acc_df


if __name__ == '__main__':
    common_names_from_index('x.csv')
