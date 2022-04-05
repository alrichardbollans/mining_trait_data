import os

from pkg_resources import resource_filename

_inputs_path = resource_filename(__name__, 'inputs')
spec_occurenc_input = os.path.join(_inputs_path, 'cleaned_species_occurences.csv')

_temp_outputs_path = resource_filename(__name__, 'temp_outputs')
spec_elevations_csv = os.path.join(_temp_outputs_path, 'cleaned_species_occurences_w_elevation.csv')

_output_path = resource_filename(__name__, 'outputs')
summary_output_csv = os.path.join(_output_path,'occurence_summary.csv')
if not os.path.isdir(_inputs_path):
    os.mkdir(_inputs_path)
if not os.path.isdir(_temp_outputs_path):
    os.mkdir(_temp_outputs_path)
if not os.path.isdir(_output_path):
    os.mkdir(_output_path)