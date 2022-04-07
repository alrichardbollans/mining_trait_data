import os

from pkg_resources import resource_filename

climate_inputs_path = resource_filename(__name__, 'inputs')
spec_occurence_input = os.path.join(climate_inputs_path, 'cleaned_species_occurences.csv')

climate_temp_outputs_path = resource_filename(__name__, 'temp_outputs')


climate_output_path = resource_filename(__name__, 'outputs')
summary_output_csv = os.path.join(climate_output_path,'occurence_summary.csv')
if not os.path.isdir(climate_inputs_path):
    os.mkdir(climate_inputs_path)
if not os.path.isdir(climate_temp_outputs_path):
    os.mkdir(climate_temp_outputs_path)
if not os.path.isdir(climate_output_path):
    os.mkdir(climate_output_path)