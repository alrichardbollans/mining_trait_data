import re

import pandas as pd
import sre_yield
# import parser object from tike
from tqdm import tqdm
from wcvp_name_matching import get_accepted_info_from_names_in_column, hybrid_characters

from read_wep import wiersema_input

# Characters that don't appear in WCVP names. There are som exceptions but these aren't in the PDF
chars_not_appearing_in_wcvp = list(set(sre_yield.AllStrings(r'[À-ÖØ-öø-ÿ\u00C0-\u024F\u1E00-\u1EFF]')))
chars_not_appearing_in_wcvp.append('African')
chars_not_appearing_in_wcvp.append('yellow')
chars_not_appearing_in_wcvp.append('Wiersema & Leόn')
chars_not_appearing_in_wcvp.append('World Economic Plants')
chars_not_appearing_in_wcvp.append('ό')
for h in hybrid_characters:
    if h in chars_not_appearing_in_wcvp:
        chars_not_appearing_in_wcvp.remove(h)
# These taxa aren't in pdf, so we can assume taxa names don't contain apostrophes
sources_of_apos_in_wcvp = ["Solanum stenotomum f. janck'o-chojllu",
                           "Solanum stenotomum f. pulu-wayk'u", "Solanum tuberosum f. jancck'o-kkoyllu",
                           "Solanum tuberosum f. janck'o-chockella",
                           "Solanum tuberosum f. janck'o-pala",
                           "Solanum tuberosum f. wila-k'oyu",
                           "Conioselinum anthriscoides 'Chuanxiong'",
                           "Solanum × juzepczukii f. ck'oyu-ckaisalla",
                           "Solanum × juzepczukii f. janck'o-ckaisalla",
                           "Antrophyum d'urvillaei",
                           ]
chars_not_appearing_in_wcvp.append("'")

# These cases break the formatting where these common names are used as subheadings.
# We check that
# This is not exhaustive and leaves out things covered by chars_not_appearing_in_wcvp e.g. African etc..
common_name_subheadings = ['abeblomst', 'abelia', 'Abelie', 'abrikos', 'abutilon', 'acacia', 'acı bakla',
                           'aconite', "adder's-tongue", 'ådselblomst', 'æble', 'ædelgran', 'aeonium',
                           'ærenpris',
                           'ært', 'ærtetræ', 'æselfoder', 'afara', 'affodil', 'Afrikaner', 'afrormosia']

print(chars_not_appearing_in_wcvp)


def check_line_could_be_part_of_a_name(given_line: str):
    possible_int = given_line.lstrip()
    possible_int = possible_int.rstrip()
    if any(x in given_line for x in chars_not_appearing_in_wcvp):
        return False
    elif any(common_names == possible_int for common_names in common_name_subheadings):
        return False
    else:
        try:
            could_be_int = int(possible_int)
        except ValueError:
            return True
        else:
            return False


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
        if ' -' in line:
            new_line = line
            count = 0
            for l in range(i + 1, len(all_text_lines)):
                next_line = all_text_lines[l]

                if ' -' not in next_line:
                    if check_line_could_be_part_of_a_name(next_line):
                        new_line += next_line
                        count += 1
                    else:
                        break
                else:
                    break
            new_lines.append(new_line)
            [next(iterable) for x in range(count)]

    return new_lines


def latin_common_names_from_index(output_csv: str = None):
    from tika import parser

    # opening pdf file with xml content
    parsed_pdf = parser.from_file(wiersema_input)
    all_text = parsed_pdf['content']

    intro_to_common_names = "Common names in the following languages are indexed " \
                            "here: Afrikaans, Czech, Danish, Dutch, English, French, German,"
    index_of_common_names_text = all_text.index(intro_to_common_names)

    arab_common_name_title = "INDEX OF ARABIC COMMON NAMES"
    index_of_arab_common_name_title = all_text.index(arab_common_name_title)
    latin_common_name_text = all_text[index_of_common_names_text:index_of_arab_common_name_title]
    split_lines = latin_common_name_text.split('\n')
    clean_lines = [l for l in split_lines if l != '']
    common_names = []
    scientific_names = []

    # Get useful lines
    common_names_lines = compress_lines_into_names(clean_lines)

    # Get common and scientific names from lines
    for line in common_names_lines:

        if ' -' in line:
            common_name = line[0:line.index(' -')]
            scientific_name = line[line.index(' -') + 3:-1]

            # Remove watermark(?) info
            if ' pjwstk' in scientific_name:
                scientific_name = scientific_name[:scientific_name.index(' pjwstk')]
            if ' UFM' in scientific_name:
                scientific_name = scientific_name[:scientific_name.index(' UFM')]

            if "," in scientific_name:
                # where genus names are abbreviated to capitals followed by a full stop, replace
                new_scientific_name = re.sub(r"[A-Z]\.", scientific_name.split()[0], scientific_name)
                new_s_names = new_scientific_name.split(sep=', ')
                scientific_names += new_s_names
                for s in new_s_names:
                    common_names.append(common_name)
            else:
                scientific_names.append(scientific_name)
                common_names.append(common_name)

    out_df = pd.DataFrame({'name': scientific_names, 'common_names': common_names})
    out_df['WEP_snippet'] = out_df.groupby(['name'])['common_names'].transform(lambda x: ':'.join(x))
    out_df.drop(columns=['common_names'], inplace=True)
    out_df.dropna(subset=['name'], inplace=True)
    out_df = out_df.drop_duplicates(subset=['name'])

    out_df['Source'] = 'WEP (Wiersema 2013)'
    acc_df = get_accepted_info_from_names_in_column(out_df, 'name', match_level='knms')
    if output_csv is not None:
        acc_df.to_csv(output_csv)
    return acc_df


def arabic_common_names_from_index(output_csv: str = None):
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
    # first do latin
    for i in tqdm(
            range(775, 1284), desc="Searching pages", ascii=False,
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

                if 'pjwstk' in scientific_name:
                    raise ValueError
                if "," in scientific_name:
                    # where genus names are abbreviated to capitals followed by a full stop, replace
                    new_scientific_name = re.sub(r"[A-Z]\.", scientific_name.split()[0], scientific_name)
                    new_s_names = new_scientific_name.split(sep=', ')
                    scientific_names += new_s_names
                    for s in new_s_names:
                        common_names.append(common_name)
                else:
                    scientific_names.append(scientific_name)
                    common_names.append(common_name)
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
    # acc_df = get_accepted_info_from_names_in_column(out_df, 'name')
    # if output_csv is not None:
    #     acc_df.to_csv(output_csv)
    # return acc_df
