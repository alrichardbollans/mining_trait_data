input_dir = here('inputs')

taxa_csv = file.path(input_dir,'app_rub_cel_taxalist.csv')

temp_output_dir = here('temp outputs')
gbif_occ_dir = file.path(temp_output_dir,'gbif_occurrences')


# path to directory where to save formatted occurrence data
temp_clean_output_dir = file.path(temp_output_dir,'cleanedOcc') 
cleaned_taxa_output_csv = file.path('outputs','cleaned_occurences.csv')

