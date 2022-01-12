import os
import subprocess

path_here = os.path.dirname(os.path.abspath(__file__))


def search_powo(search_terms: str, output_file: str):
    '''

    :param search_terms: string of terms e.g. 'poison,poisonous,toxic,deadly'
    :param output_file:
    :return:
    '''
    r_script = os.path.join(path_here, 'powo_search.R')
    command = f'Rscript "{r_script}" --out "{output_file}" --searchterms "{search_terms}"'

    subprocess.call(command, shell=True)
