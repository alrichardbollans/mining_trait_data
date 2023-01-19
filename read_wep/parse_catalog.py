import pandas as pd
from tqdm import tqdm
from typing import List

from wcvp_download import get_all_taxa
from wcvp_name_matching import get_accepted_info_from_names_in_column

from read_wep import wiersema_input

categories = ['CN', 'ECON', 'DIST', 'SYN']
parenthesised_words = ['fiber', 'wood', 'sugar', 'ornamental', 'shade/shelter', 'seed contam.', 'folklore',
                       'mammals', 'flavoring', 'erosion control', 'potential as forage', 'crop diseases',
                       'also poss. seed contam.', 'potential as soil improver'
                                                  'vegetable']


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


def get_scientific_names_from_property(category: str, property: str = None,
                                       output_csv: str = None) -> pd.DataFrame:
    if property is None and category != 'CN':
        raise ValueError(f'Need to provide property for category: {category}')
    if category == 'CN' and property is not None:
        raise ValueError(f'Cant provide property for category: {category}')
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
        if property is not None:
            if property in line and category + ':' in line:
                scientific_names.append(retrieve_name_from_property_line(i, econ_lines, genus_list))

        elif category == 'CN':
            if category + ':' in line:
                scientific_names.append(retrieve_name_from_property_line(i, econ_lines, genus_list))
    out_df = pd.DataFrame({'name': scientific_names})
    out_df['Source'] = 'WEP (Wiersema 2013)'
    acc_df = get_accepted_info_from_names_in_column(out_df, 'name')
    if output_csv is not None:
        acc_df.to_csv(output_csv)
    return acc_df


def poisons_from_wiersema(output_csv: str):
    poisons = get_scientific_names_from_property('ECON', 'Poison', output_csv)
    return poisons


def get_traditional_medicines_from_wiersema(output_csv: str):
    medicines = get_scientific_names_from_property('ECON', 'Medic. (folklore)', output_csv)
    return medicines


def get_commonnames_from_catalog(output_csv: str):
    common_names = get_scientific_names_from_property('CN', output_csv=output_csv)
    return common_names
