import pandas as pd
# import parser object from tike
from tqdm import tqdm
from typing import List

from wcvp_download import get_all_taxa
from wcvp_name_matching import get_accepted_info_from_names_in_column

from read_pdfs import wiersema_input

categories = ['CN', 'ECON', 'DIST', 'SYN']
parenthesised_words = ['fiber', 'wood', 'sugar', 'ornamental', 'shade/shelter', 'seed contam.', 'folklore',
                       'mammals', 'flavoring', 'erosion control', 'potential as forage', 'crop diseases',
                       'also poss. seed contam.', 'potential as soil improver'
                                                  'vegetable']


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


def common_names_from_wiersema(output_csv: str):
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
    # This catches most of these cases but it is not critical if we miss some
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
    out_df.to_csv(output_csv)
    return out_df


def not_possible_name_check(line, genus_list: List[str]):
    # Checks if line is not a name first based on specifics to formatting of pdf, then if any
    # genus name is in the line
    if len(line) == 0:
        return True
    if (line[0].islower() or any(non_name_punc in line for non_name_punc in [':', ';', '=']) or any(
            c + ':' in line for c in categories) or '[' in line or any(
        '(' + w in line for w in parenthesised_words) or any(
        w + ')' in line for w in parenthesised_words) or any(
        heading in line for heading in ['Wiersema & León', 'World Economic Plants']) or any(
        problem_line_snippets in line for problem_line_snippets in
        ['wallflower cottonbush', 'touriga, beautyleaf, Borneo-mahogany', 'weißer Mahagonibaum',
         'erva-das-lombrigas, erva-de-bic', 'laurel fig,', 'dry-whiskey,', 'chamomile,', 'Indian-mint,',
         'S. M. Almeida ex Sanjappa & Predeep', 'East Indian rose bay,', 'jequirity,'])):
        return True
    elif any(g in line.split() for g in genus_list):
        return False

    else:
        return True


def retrieve_name_from_property_line(line_index, all_lines, genus_list: List[str]):
    i = 1
    previous_line = all_lines[line_index - 1]
    while not_possible_name_check(previous_line, genus_list):
        i += 1
        previous_line = all_lines[line_index - i]
    return previous_line


def compress_lines_into_categories(all_text_lines, genus_list: List[str]):
    new_lines = []
    iterable = iter(range(len(all_text_lines)))
    print('total its: 79581')
    for i in tqdm(
            iterable, desc="compress_lines_into_categories", ascii=False,
            ncols=72):
        line = all_text_lines[i]
        if line == '' or line == ' ':
            continue
        elif any(c + ':' in line for c in categories):
            new_line = line
            count = 0
            for l in range(i + 1, len(all_text_lines)):
                next_line = all_text_lines[l]
                if not_possible_name_check(next_line, genus_list):
                    if any(c + ':' in next_line for c in categories):
                        break
                    else:
                        new_line += next_line
                        count += 1
                else:
                    break
            new_lines.append(new_line)
            [next(iterable) for x in range(count)]
        else:
            new_lines.append(line)

    return new_lines


def get_scientific_names_from_property(category: str, property: str, output_csv: str):
    genus_list = get_all_taxa(ranks=['Genus'])['taxon_name'].unique().tolist()
    from tika import parser
    parsed_pdf = parser.from_file(wiersema_input)
    all_text = parsed_pdf['content']

    intro_to_common_names = "Common names in the following languages are indexed " \
                            "here: Afrikaans, Czech, Danish, Dutch, English, French, German,"
    index_of_common_names_text = all_text.index(intro_to_common_names)

    intro_to_econ = "Dr. Takasi Yamazaki – Tokyo, JAPAN –"
    index_of_econ_text = all_text.index(intro_to_econ)
    econ_text = all_text[index_of_econ_text:index_of_common_names_text]
    split_lines = econ_text.split('\n')
    econ_lines = compress_lines_into_categories(split_lines, genus_list)

    scientific_names = []
    for i in tqdm(
            range(len(econ_lines)), desc="searching through categories", ascii=False,
            ncols=72):
        line = econ_lines[i]
        if property in line and category + ':' in line:
            scientific_names.append(retrieve_name_from_property_line(i, econ_lines, genus_list))

    out_df = pd.DataFrame({'name': scientific_names})
    out_df['Source'] = 'WEP (Wiersema 2013)'
    acc_df = get_accepted_info_from_names_in_column(out_df, 'name')
    acc_df.to_csv(output_csv)
    return acc_df


def poisons_from_wiersema(output_csv: str):
    poisons = get_scientific_names_from_property('ECON', 'Poison', output_csv)
    return poisons


def get_traditional_medicines_from_wiersema(output_csv: str):
    medicines = get_scientific_names_from_property('ECON', 'Medic. (folklore)', output_csv)
    return medicines


if __name__ == '__main__':
    common_names_from_wiersema('x.csv')
